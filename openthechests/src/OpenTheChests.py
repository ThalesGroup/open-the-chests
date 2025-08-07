from openthechests.openthechests.src.elements.Generator import Generator
from openthechests.openthechests.src.elements.InteractiveBox import InteractiveBox
from openthechests.openthechests.src.elements.Parser import Parser
from openthechests.openthechests.src.elements.Pattern import Pattern
from openthechests.openthechests.src.utils.helper_functions import to_stb3_obs_format


class OpenTheChests:
    """
    OpenTheChests is a symbolic event-based interactive environment where players observe timed events
    and must open boxes (chests) at the right time based on symbolic and temporal cues.

    It is used for tasks involving pattern recognition, temporal reasoning, and decision-making.
    The environment generates complex, noisy event sequences and provides symbolic observations
    and contextual cues.

    Attributes
    ----------
    discrete : bool
        Whether the environment uses discrete (integer) actions.
    verbose : bool
        Whether to print debug information.
    done : bool
        Whether the environment has reached a terminal state.
    patterns : list[Pattern]
        The list of Pattern objects defining event structures for each box.
    boxes : list[InteractiveBox]
        List of interactive boxes that can be opened by pressing buttons.
    parser : Parser
        Used to instantiate events, generate noise, and convert event observations to a labeled format.
    generator : Generator
        Responsible for producing timelines of events (both real and noisy) from patterns.

    Hidden Attributes
    -----------------
    _timeout_threshold : int
        Max number of allowed box deactivations before ending the episode.
    _action : list[int]
        The last action taken in the environment.
    _context : Event
        The most recent event in the environment timeline.
    _stb3 : bool
        Whether to format observations for Stable Baselines 3 compatibility.
    _time : float
        The current simulated time in the environment.
    _num_boxes : int
        Number of interactive boxes in the environment.

    Methods
    -------
    reset() -> tuple
        Resets the environment, including boxes, patterns, and timeline.
    step(action) -> tuple
        Applies an action, advances time, updates the environment, and returns observation, reward, done, and info.
    get_observations() -> dict
        Returns the current state and context as the observation.
    uses_discrete_actions() -> bool
        Returns whether the environment expects discrete actions.
    get_all_types() -> list
        Returns all event and noise types used in the environment.
    get_num_boxes() -> int
        Returns the number of interactive boxes (chests) in the environment.
    check_end() -> bool
        Checks whether the episode has ended based on conditions.
    render() -> None
        Updates the GUI display (if applicable).

    Hidden Methods
    --------------
    _internal_step() -> None
        Advances the timeline by one step and updates context and box states.
    _advance_timeline() -> dict
        Gets the next event from the generator and moves time forward.
    _update_boxes(signal: dict) -> None
        Applies the signal to all boxes to update their internal state.
    _apply_action(action: list[int]) -> int
        Applies a user action (open box) and returns the resulting reward.
    """

    def __init__(self,
                 instructions: list,
                 all_event_types: list,
                 all_event_attributes: dict,
                 all_noise_types: list,
                 all_noise_attributes: dict,
                 verbose: bool,
                 timeout_threshold: int = 30,
                 stb3: bool = False,
                 discrete: bool = False):
        """
        Initializes the environment with a list of event patterns and configuration.

        Parameters
        ----------
        instructions : list
            Instruction sets used to define behavior for each box.
        all_event_types : list
            List of all symbolic event types.
        all_event_attributes : dict
            Mapping from attribute name to list of valid values for event types.
        all_noise_types : list
            List of event types used exclusively for noise generation.
        all_noise_attributes : dict
            Mapping from attribute name to valid values for noise types.
        verbose : bool
            Whether to enable verbose debug printing.
        timeout_threshold : int
            Max number of total box deactivations before ending the episode.
        stb3 : bool
            Whether to format observations to be SB3-compatible.
        discrete : bool
            Whether the environment uses discrete actions (integers) instead of binary vectors.
        """

        self._timeout_threshold = timeout_threshold
        self._action = None
        self._context = None
        self._stb3 = stb3
        self._time = 0
        self._num_boxes = len(instructions)

        self.discrete = discrete
        self.verbose = verbose
        self.done = False
        self.patterns = [Pattern(id=idx, instruction=instr) for idx, instr in enumerate(instructions)]
        self.boxes = [InteractiveBox(id=pattern.id, verbose=self.verbose) for pattern in self.patterns]
        self.parser = Parser(all_event_types=all_event_types,
                             all_noise_types=all_noise_types,
                             all_event_attributes=all_event_attributes,
                             all_noise_attributes=all_noise_attributes)
        self.generator = Generator(parser=self.parser, patterns=self.patterns, verbose=self.verbose)

        if self.verbose:
            print(f"All event types : {all_event_types}")
            print(f"All noise types : {all_noise_types}")
            print(f"All event attributes : {all_event_attributes}")
            print(f"All noise attributes : {all_noise_attributes}")
            print(f"Initialising {self._num_boxes} boxes.")

    def uses_discrete_actions(self):
        """
        Returns whether the environment is configured to use discrete actions.

        Returns
        -------
        bool
            True if discrete actions are enabled, False otherwise.
        """
        return self.discrete

    def get_all_types(self):
        """
        Returns all event and noise types defined in the parser.

        Returns
        -------
        list[str]
            Combined list of event types and noise types.
        """
        return self.parser.all_event_types + self.parser.all_noise_types

    def get_num_boxes(self):
        """
        Returns the number of interactive boxes in the environment.

        Returns
        -------
        int
            Number of boxes.
        """
        return self._num_boxes

    def reset(self):
        """
        Fully resets the environment, boxes, and event timeline.
        Restarts time, resets each box and its pattern, and refills the timeline of events.
        Gets one observation of the newly reset environment.

        Returns
        -------
        tuple[dict, dict]
            Observation and an empty info dictionary.
        """

        if self.verbose:
            print("Starting Reset")
        self._time = 0

        self.generator.reset()

        for box in self.boxes:
            box.reset()

        self._internal_step()

        obs = self.get_observations()

        if self.verbose:
            print("Reset Done.")

        return obs

    def step(self, action):
        """
        Advances the environment by one interaction step based on the provided action.

        This method performs:
        1. **Action parsing**: Converts the action into a binary list if using discrete actions.
        2. **Action application**: Applies the action to boxes (e.g., attempts to open them) and calculates rewards.
        3. **Timeline advancement**: Internally advances the event timeline and updates the current context.
        4. **Observation generation**: Collects the current state and context for the agent.

        Parameters
        ----------
        action : list[int] or int
            - If `discrete` is False: a binary list of length equal to the number of boxes,
              where each index indicates whether to press a box's button.
            - If `discrete` is True: an integer representing the binary-encoded action.

        Returns
        -------
        tuple
            (observation, reward, done, info)
            - **observation** : dict
                The current observation including box states and context.
            - **reward** : int
                The cumulative reward from all box interactions in this step.
            - **done** : bool
                Whether the episode has ended (all boxes opened or max deactivations reached).
            - **info** : dict
                Placeholder for additional metadata (currently empty).
        """

        if self.verbose:
            print("\nStart Step")

        # If action is discrete, decode it into a binary list of button presses
        if self.discrete:
            action = [int(x) for x in bin(action)[2:]]
            action = (self._num_boxes - len(action)) * [0] + action

        # Apply the action and compute reward
        reward = self._apply_action(action=action)

        # Advance environment timeline and update context
        self._internal_step()

        # Collect updated observation
        obs = self.get_observations()

        # Check whether the episode should end
        self.done = self.check_end()

        if self.verbose:
            print("Step Done \n")

        return obs, reward, self.done, dict()

    def get_observations(self):
        """
        Returns the current observation available to the agent/player.

        The observation includes:
        - The **state** of all boxes: whether each is active or open (as boolean lists).
        - The **context**, which is the most recent event, label-encoded based on the parser configuration.

        Example output:
        {
            'state': {
                'active': [True, False, True],
                'open': [False, True, False]
            },
            'context': Event(
                type=2,
                attributes={'bg': 6, 'fg': 3},
                start=0.0,
                end=4.58
            )
        }

        Notes
        -----
        - If `self._stb3` is True, the observation will be flattened into a single-level dictionary
          to ensure compatibility with Stable Baselines3 (which does not support nested dicts).
        - Labeling converts string-based event types/attributes into integer indices based on initialization data.

        Returns
        -------
        dict
            The observation dictionary containing box state and the current labeled context event.
        """
        active = [box.is_active() for box in self.boxes]
        open_ = [box.is_open() for box in self.boxes]

        box_states = {"active": active, "open": open_}
        labeled_context = self.parser.event_to_labelled(self._context)

        obs = {"state": box_states, "context": labeled_context}

        if self._stb3:
            obs = to_stb3_obs_format(observation=obs)

        return obs

    def _internal_step(self):
        """
        Executes one internal step to advance the environment timeline and update context.
        Update box states to take into account new information.
        """
        if self.verbose:
            print("Making one internal step to get context and advance timeline.")

        signal = self._advance_timeline()
        self._update_boxes(signal=signal)

    def _advance_timeline(self):
        """
        Advances the environment timeline by retrieving and applying the next event.

        This method:
        - Selects the next event to play across all pattern timelines (based on the earliest end time).
        - Updates the internal `context` to this new event.
        - Advances the environment's internal clock (`_time`) to the end of the current event.
        - Collects and returns a signal dictionary indicating which patterns (boxes) are now active or satisfied.

        The signal is used to update the states of the interactive boxes in the environment.

        Returns
        -------
        dict
            A dictionary mapping pattern IDs to signal lists (e.g., {"satisfied", "active"}).
        """

        if self.verbose:
            print(f"Active timeline {self.generator.get_timeline()}")

        next_event, signal = self.generator.next_event()

        if next_event.type != "Empty":
            self._context = next_event
            self._time = self._context.end

        if self.verbose:
            print(f"The last observed event ends at {round(self._time, 3)}")
            print(f"Advancing _time to {round(self._time, 3)}")
            print(f"Observing context {self._context}")

        return signal

    def _update_boxes(self, signal=None):
        """
        Updates the state of each interactive box using the provided signal.

        Each box receives its corresponding signal based on its pattern ID.
        If a box has no signal in the current step, it is updated with an empty list.

        Parameters
        ----------
        signal : dict, optional
            A dictionary mapping box (pattern) IDs to a list of signals (e.g., {"active", "satisfied"}).
            Defaults to an empty dictionary if not provided.
        """
        signal = signal or {}
        for box in self.boxes:
            box.update(signal=signal.get(box.id, []))

    def _apply_action(self, action):
        """
        Processes the player's action by interacting with the boxes and computing the resulting reward.

        Each element in the `action` list corresponds to whether a button press is attempted on a specific box:
        - 1: attempt to press the box's button.
        - 0: do not press the box's button.

        Reward logic:
        - **+1**: Correctly pressed a box when it was ready, causing it to open.
        - **-1**: Incorrect press (e.g., pressing a box that wasn't ready) or failing to press a ready box.
        - **0**: No action was taken on a box that wasn't ready.

        If a box is successfully opened, its future timeline is disabled.

        Parameters
        ----------
        action : list[int]
            A list of 0s and 1s representing the decision to press or not press each box's button.
            Must be the same length as the number of boxes in the environment.

        Returns
        -------
        int
            The total reward obtained from this step across all boxes.

        Raises
        ------
        AssertionError
            If the length of the action list does not match the number of boxes.
        """
        assert len(action) == self._num_boxes, f"Got action of size {len(action)} while boxes are {self._num_boxes}."

        self._action = action
        if self.verbose:
            print(f"Applying action {action}.")

        reward = []

        for box_id in range(len(action)):
            current_box = self.boxes[box_id]

            # Case: attempt to press the box button
            if action[box_id] == 1:
                opened = current_box.press_button()
                if opened:
                    self.generator.disable_timeline(pattern_id=box_id)
                    reward.append(1)
                else:
                    reward.append(-1)

            # Case: no press, but check if box should have been opened
            else:
                if current_box.is_ready():
                    reward.append(-1)
                else:
                    reward.append(0)

        return sum(reward)

    def check_end(self):
        """
        Determines whether the environment episode should terminate.

        The environment is considered finished in either of the following scenarios:
        1. **All boxes are opened**: Every box has been successfully opened by the agent.
        2. **Too many deactivations**: The total number of deactivations across all boxes
           exceeds the environment's `_timeout_threshold`, signaling failure.

        This function is typically called at the end of each step to update the `done` status.

        Returns
        -------
        bool
            True if the environment is done (either all boxes opened or deactivation threshold reached),
            False otherwise.
        """
        all_end = all([box.is_open() for box in self.boxes])
        all_deactivations = sum([b.num_deactivations for b in self.boxes])
        return all_end or (all_deactivations >= self._timeout_threshold)

    def render(self):
        """
        Update GUI with all information needed to display environment and update display step.
        """
        pass
