from openthechests.src.elements.Generator import Generator
from openthechests.src.elements.Parser import Parser
from openthechests.src.elements.InteractiveBox import InteractiveBox
from openthechests.src.elements.Pattern import Pattern
from openthechests.src.utils.helper_functions import to_stb3_obs_format


class OpenTheChests:
    """
    Environment that allows interaction with and opening of boxes after observing symbols.
    Example of environment usage and initialization in examples.create_env.

    Attributes:
    -----------
    discrete : bool
        Flag to determine if actions are in integer format.
    verbose : bool
        Flag to enable detailed print statements for debugging.
    done : bool
        Flag to indicate if the environment episode is done.
    patterns : list
        The list of patterns used to define the behavior of the boxes.
    boxes : list
        The list of InteractiveBox objects in the environment.
    parser : Parser
        The parser used to interpret event and noise information.
    generator : Generator
        The generator used to create event stacks based on patterns.

    Hidden Attributes:
    ------------------
    _timeout_threshold : int
        The threshold for the number of times boxes can be collectively deactivated before ending the game.
    _action : list
        The current action being applied in the environment.
    _context : Event
        The current event context in the environment.
    _stb3 : bool
        Flag to determine if the environment should be compatible with Stable Baselines 3.
    _time : float
        The current time in the environment.
    _num_boxes : int
        The number of boxes in the environment.

    Methods:
    --------
    uses_discrete_actions():
        Returns whether the environment uses discrete actions.
    get_all_types():
        Returns a list of all event and noise types.
    get_num_boxes():
        Returns the number of boxes in the environment.
    reset():
        Resets the environment to its initial state.
    step(action):
        Advances the environment by one step using the selected action.
    get_observations():
        Returns the current observations of the environment.
    check_end():
        Verifies if it is time to send a done signal indicating the end of the game.

    Hidden Methods:
    ---------------
    _internal_step():
        Executes one internal step to advance the environment timeline and update context.
    _advance_timeline():
        Advances the internal environment evolution by getting the next event.
    _update_boxes(signal):
        Updates the states of all boxes based on the current environment time and evolution.
    _apply_action(action):
        Applies the given action to the system and updates the environment according to action effects.
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
        Initializes the OpenTheChests environment with the given parameters.

        :param instructions: list
            List of commands allowing to define behavior for each box.
        :param all_event_types: list
            List of all possible event types that can take place.
        :param all_event_attributes: dict
            Dictionary of all event types with a corresponding list of possible values.
        :param all_noise_types: list
            List of all possible types to be used for noise generation only.
        :param all_noise_attributes: dict
            Dictionary of all possible types to be used for noise generation only.
        :param verbose: bool
            Flag to enable detailed print statements for debugging.
        :param timeout_threshold: int, optional
            The threshold for the number of times boxes can be collectively deactivated before ending the game (default is 30).
        :param stb3: bool, optional
            Flag to determine if the environment should be compatible with Stable Baselines 3 (default is False).
        :param discrete: bool, optional
            Flag to determine if actions are in integer format (default is False).

        Note: When accepting integer actions, each value will be transformed into its corresponding binary number.
        """

        self._timeout_threshold = timeout_threshold
        self.discrete = discrete
        self._action = None
        self._context = None
        self._stb3 = stb3
        self._time = 0
        self.verbose = verbose
        self.done = False
        self._num_boxes = len(instructions)

        self.patterns = [Pattern(id=idx, instruction=instr) for idx, instr in enumerate(instructions)]
        self.boxes = [InteractiveBox(id=pattern.id, verbose=self.verbose) for pattern in self.patterns]

        self.parser = Parser(all_event_types=all_event_types,
                             all_noise_types=all_noise_types,
                             all_event_attributes=all_event_attributes,
                             all_noise_attributes=all_noise_attributes)
        self.generator = Generator(parser=self.parser, patterns=self.patterns, verbose=self.verbose)
        # self.GUI = BoxEventGUI(num_patterns=self._num_boxes,
        #                      attr_to_color=self.parser.all_attributes)

        if self.verbose:
            print(f"All event types : {all_event_types}")
            print(f"All noise types : {all_noise_types}")
            print(f"All event attributes : {all_event_attributes}")
            print(f"All noise attributes : {all_noise_attributes}")
            print(f"Initialising {self._num_boxes} boxes with patterns")

    def uses_discrete_actions(self):
        return self.discrete

    def get_all_types(self):
        return self.parser.all_event_types + self.parser.all_noise_types

    def get_num_boxes(self):
        return self._num_boxes

    def reset(self):
        """
        Resets the environment to its initial state.
        Restarts time, resets each box and its pattern, and refills the timeline of events.
        Gets one observation of the newly reset environment.

        Note: The observation form may vary depending on the _stb3 parameter.

        :return: dict
            The first observation of the newly reset environment.
        """

        if self.verbose:
            print("Starting Reset")
        self._time = 0

        self.generator.reset()

        for box in self.boxes:
            box.reset()
            # TODO priority 2: should boxes be active from the beginning?
            box._activate()

        self._internal_step()

        obs = self.get_observations()

        if self.verbose:
            print("Reset Done")

        return obs

    def step(self, action):
        """
        Moves the environment forward by one step using the selected action.
        The forward move consists of three steps:
         - Apply the action to the environment
         - Advance the environment's internal interactions
         - Extract observation and return it to the user

        :param action: list or int
            List of box ids to attempt to open, or an integer action if discrete actions are used.
        :return: tuple
            A tuple containing the observation, reward, done flag, and an empty dictionary.
        """

        if self.verbose:
            print("\nStart Step")

        # if action is discrete turn it into a vector
        if self.discrete:
            action = [int(x) for x in bin(action)[2:]]
            action = (self._num_boxes - len(action)) * [0] + action
        # apply action and collect reward
        reward = self._apply_action(action=action)

        # advance environment and collect context
        self._internal_step()
        obs = self.get_observations()

        self.done = self.check_end()

        reward = 1 if self.done else 0

        if self.verbose:
            print("Step Done \n")

        # TODO (priority 2) fill info dict? use it somehow?
        return obs, reward, self.done, dict()

    def get_observations(self):
        """
        Returns the last observation of information visible to a player.
        The return contains:
            - State information under the form of binary vectors showing if boxes are active or open
            - Context information giving the last observed event in its labeled form

        Example:
        {'state':
            {'active': [True, True, True], 'open': [False, False, False]},
        'context':
            Event('e_type': 2, 'attr': {'bg': 6, 'fg': 3}, 'start' : 0, 'end': 4.582803102406337)
        }

        Note: Depending on the _stb3 parameter, the returned dictionary can have different forms:
            - _stb3 == True: one-level dictionary with entries for each information
            - otherwise: two-level dictionary
        This is because stable baselines do not accept multiple-level dictionaries as input,
        so the output is transformed into a one-level dictionary with multiple values.

        :return: dict
            Dictionary containing environment information.
        """
        active = []
        open = []

        # TODO (priority 3) this can be optimised
        for box_id in range(self._num_boxes):
            active.append(self.boxes[box_id].is_active())
            open.append(self.boxes[box_id].is_open())

        box_states = {"active": active, "open": open}

        # TODO priority 3: rethink labeling
        obs = {"state": box_states, "context": self.parser.event_to_labelled(self._context
                                                                             )}

        if self._stb3:
            obs = to_stb3_obs_format(observation=obs)
        return obs

    def _internal_step(self):
        """
        Executes one internal step to advance the environment timeline and update context.
        Update box states to take into account new information.
        """
        if self.verbose:
            print("Making one internal step to get context and advance timeline")

        signal = self._advance_timeline()
        self._update_boxes(signal=signal)

    def _advance_timeline(self):
        """
        Advances the internal environment evolution by getting the next event.
        Start by getting the next event to be played by selecting from the timeline of next events the one with the
        smallest ending time.
        Add this event as the current context and advance the current time to the end of the event.
        Check if any other boxes are satisfied by this event.

        :return: dict
            Signal dictionary indicating which boxes are satisfied or active.
        """

        if self.verbose:
            print(f"Active timeline {self.generator.get_timeline()}")

        next_event, signal = self.generator.next_event()
        # bug_print(signal)
        if next_event.type != "Empty":
            self._context = next_event
            self._time = self._context.end

        if self.verbose:
            print(f"Finding closes end value {self._time}")
            print(f"Advancing _time to {self._time}")
            print(f"Observing context {self._context}")

        return signal

    def _update_boxes(self, signal=[]):
        """
        Updates the states of all boxes based on the current environment time and evolution.

        :param signal: list
            Signal list indicating which boxes are satisfied or active.
        """
        for box in self.boxes:
            box.update(signal=[] if box.id not in signal else signal[box.id])

    def _apply_action(self, action):
        """
        Applies the given action to the system and updates the environment according to action effects.
        Attempts to open the corresponding box if the action at index i is set to 1.
        If the box is opened, disables its timeline and gives a positive reward.
        Otherwise, if the button is wrongly pressed or the chest is ready to open yet ignored, a reward of -1 is applied.
        In all other cases, the reward is 0.

        :param action: list
            The action to apply.
        :return: int
            Reward obtained for the selected action.
        """
        assert len(action) == self._num_boxes, f"Got action of size {len(action)} while boxes are {self._num_boxes}."

        # TODO (priority 3) make code prettier reduce all ifs and separate press and reward if possible
        self._action = action
        if self.verbose:
            print(f"Applying action {action}")
        reward = []
        for box_id in range(len(action)):
            current_box = self.boxes[box_id]
            if action[box_id] == 1:
                opened = current_box.press_button()
                if opened:
                    self.generator.disable_timeline(pattern_id=box_id)
                    reward.append(1)
                else:
                    reward.append(-1)
            else:
                if current_box.is_ready():
                    reward.append(-1)
                else:
                    reward.append(0)
        return sum(reward)

    def check_end(self):
        """
        Verifies if it is time to send a done signal indicating the end of the game.
        A done signal can be sent in one of two cases:
            - All boxes have been opened, indicating the end of the game.
            - All boxes have been collectively deactivated more than _timeout_threshold times.

        :return: bool
            Boolean indicating the end of the game.
        """
        all_end = all([box.is_open() for box in self.boxes])
        all_deactivations = sum([b.num_deactivations for b in self.boxes])
        return all_end or (all_deactivations >= self._timeout_threshold)

    def render(self):
        """
        Update GUI with all information needed to display environment and update display step.
        """
        self.GUI.add_event_to_history(self._context)
        self.GUI.update_variable("context", self._context)
        self.GUI.update_variable("_time", self._time)
        self.GUI.update_variable("last_action", self._action)
        self.GUI.update_variable("boxes", self.boxes)
        self.GUI.update_variable("patterns", self.patterns)
        self.GUI.step()
