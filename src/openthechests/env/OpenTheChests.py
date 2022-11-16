from typing import List
from src.openthechests.env.GUI import BoxEventGUI
from src.openthechests.env.elements.Parser import Parser
from src.openthechests.env.elements.InteractiveBox import InteractiveBox
from src.openthechests.env.elements.Pattern import Pattern
from src.openthechests.env.utils.helper_functions import to_stb3_obs_format


class Environment:
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
        Environment that allows to interact and open boxes after observing symbols.
        Example of environment usage and initialisation in examples.create_env .

        :param instructions: List of commands allowing to define patterns for each box
        :param all_event_types: List of all possible event types that can take place
        :param all_event_attributes: Dictionary of al event types with a corresponding list of possible values
        :param all_noise_types: List of all possible types to be used for noise generation only
        :param all_noise_attributes: List of all possible types to be used for noise generation only
        :param discrete: Accept actions under integer format instead of binary vector.
                Discrete actions are converted to their corresponding binary value and used as vectors.
        :param verbose: Print details when executing for debugging
        :param stb3: Use environment with stable baselines 3

        Note: When accepting integer actions, each value will be transformed into its corresponding binary number
        """

        self.timeout_threshold = timeout_threshold
        self.discrete = discrete
        self.action = None
        self.context = None
        self.last_action = None
        self.stb3 = stb3
        self.time = 0
        self.verbose = verbose
        self.done = False
        self.num_boxes = len(instructions)

        self.parser = Parser(all_event_types, all_noise_types, all_event_attributes, all_noise_attributes)
        self.GUI = BoxEventGUI(self.num_boxes, self.parser.all_attributes)

        self.patterns = [Pattern(self.parser, instr, self.verbose) for instr in instructions]
        self.timeline = {}

        self.boxes = [InteractiveBox(idx, pattern, self.verbose) for idx, pattern in enumerate(self.patterns)]

        if self.verbose:
            print(f"All event types : {all_event_types}")
            print(f"All noise types : {all_noise_types}")
            print(f"All event attributes : {all_event_attributes}")
            print(f"All noise attributes : {all_noise_attributes}")
            print(f"Initialising {self.num_boxes} boxes with patterns")

    def reset(self):
        """
        Reset the environment.
        Restart time, reset each box and its pattern and refill the timeline of events.
        Get one observation of the newly reset environment.

        Note: observation form may vary depending on the stb3 parameter.

        :return: The first observation of the newly reset environment.
        """

        if self.verbose:
            print("Starting Reset")
        self.time = 0
        for box in self.boxes:
            box.reset(self.time)
            self.timeline[box.id] = box.pattern.get_next()

        self._internal_step()

        obs = self.get_observations()

        if self.verbose:
            print("Reset Done")

        return obs

    def step(self, action: List[int]):
        """
        Move forward the environment by one step using the selected action.
        Forward move consists in three steps:
         - Apply the action to the environment
         - Advance environment's internal interactions
         - Extract observation and return it to the user

        :param action: List of box ids to attempt to open
        :return: Reward obtained from acting and context at the end of the environment step
        """

        if self.verbose:
            print("\nStart Step")

        # if action is discrete turn it into a vector
        if self.discrete:
            action = [int(x) for x in bin(action)[2:]]
            action = (self.num_boxes - len(action)) * [0] + action
        # apply action and collect reward
        reward = self._apply_action(action)

        # advance environment and collect context
        self._internal_step()
        obs = self.get_observations()

        self.done = self.check_end()

        if self.verbose:
            print("Step Done \n")

        # TODO (priority 2) fill info dict? use it somehow?
        return obs, reward, self.done, dict()

    def get_observations(self):
        """
        Return the last observation of information visible to a player.
        Return contains:
            - State information  under the form of binary vectors showing if @self.boxes are active or open
            - Context information giving the last observed event in its labeled form

        Example:
        {'state':
            {'active': [True, True, True], 'open': [False, False, False]},
        'context':
            Event('e_type': 2, 'attr': {'bg': 6, 'fg': 3}, 'start' : 0, 'end': 4.582803102406337)
        }

        Note depending on the @stb3 parameter the returned dictionary can have different forms:
            - @stb3 == True : one level dictionary with entries for each information
            - otherwise : two level dictionary
        This is because stable baselines does not accept multiple level dictionaries as input,
        we thus transform our output into a one level dictionary with multiple values.

        :return: Dictionary containing environment information
        """
        active = []
        open = []

        # TODO (priority 3) this can be optimised
        for box_id in range(self.num_boxes):
            active.append(self.boxes[box_id].is_active())
            open.append(self.boxes[box_id].is_open())

        box_states = {"active": active, "open": open}

        obs = {"state": box_states, "context": self.context}

        if self.stb3:
            obs = to_stb3_obs_format(obs)
        return obs

    def _internal_step(self):
        """
        Execute one internal step to advance the environment timeline and update context.
        Update box states to take into account new information.
        """
        if self.verbose:
            print("Making one internal step to get context and advance timeline")

        self._advance_timeline()
        self._update_boxes(self.time)

    def _advance_timeline(self):
        # TODO (priority 4) doc
        """
        Advance internal environment evolution.
        Start by getting the next event to be played by select from the timeline of next events the one with the smallest
        ending time. Add this event as the current context and advance the current time to the end of the event.
        Check if any other boxes are satisfied by this event.
        """

        if self.verbose:
            print(f"Active timeline {self.timeline}")

        if self.timeline:
            ending_box_id = min(self.timeline, key=self.timeline.get)
            self.context = self.timeline[ending_box_id]
            self.time = self.context.end
            all_satisfied_boxes = [box_id for box_id in self.timeline if self.timeline[box_id] == self.context]
            for satisfied_box_id in all_satisfied_boxes:
                event = self.boxes[satisfied_box_id].pattern.get_next()
                self.timeline[satisfied_box_id] = event

            if self.verbose:
                print(f"Finding closes end value {self.time}")
                print(f"Advancing time to {self.time}")
                print(f"Sampling from boxes {ending_box_id}")
                print(f"Observing context {self.context}")
        else:
            if self.verbose:
                print("Timeline is empty as all boxes are opened")

    def _update_boxes(self, t_current):
        # TODO (priority 4) doc and optimise
        """
        Update all boxes states to be coherent with current environment time and evolution.

        :param t_current: The current system time used to re-activate boxes if needed.
        """
        for box in self.boxes:
            box.update(t_current)

    def _apply_action(self, action):
        """
        Apply given action to system and update environment according to action effects.
        Attempt to open corresponding box if the action at index i is set to 1.
        If the box is opened disable its timeline and give a positive reward.
        Otherwise, if the button is wrongly pressed or the chest is ready to open yet ignored a reward of -1 is applied.
        In all other cases reward is 0.

        :param action: The action to apply
        :return: Reward obtained for the selected action.
        """
        # TODO (priority 4) doc
        # TODO (priority 2) make code prettier reduce all ifs and separate press and reward if possible
        self.action = action
        if self.verbose:
            print(f"Applying action {action}")
        reward = []
        for box_id in range(len(action)):
            current_box = self.boxes[box_id]
            if action[box_id] == 1:
                opened = current_box.press_button()
                if opened:
                    self._disable_timeline(box_id)
                    reward.append(1)
                else:
                    reward.append(-1)
            else:
                if current_box.is_ready():
                    reward.append(-1)
                else:
                    reward.append(0)
        return sum(reward)

    def _disable_timeline(self, box_id):
        """
        Remove the box_id from the timeline dictionary, disabling its evolution.
        :param box_id: The box id to remove from the game.
        """
        # TODO (priority 3) sent this to get_next possibly via box opening? remove event stack to prevent problems?
        self.timeline.pop(box_id, None)

    def check_end(self):
        """
        Verify if it's time to send a done signal indicating the end of the game.
        A done signal can be sent in one of two case:
            - All boxes have been opened giving the end of the game.
            - All boxes have been collectively deactivated more than @self.timeout_threshold times.

        :return: Boolean indicating the end of the game
        """
        all_end = all([box.is_open() for box in self.boxes])
        all_deactivations = sum([b.num_deactivations for b in self.boxes])
        return all_end or (all_deactivations >= self.timeout_threshold)

    def render(self):
        """
        Update GUI with all information needed to display environment and update display step.
        """
        self.GUI.add_event_to_history(self.context)
        self.GUI.update_variable("context", self.context)
        self.GUI.update_variable("time", self.time)
        self.GUI.update_variable("last_action", self.action)
        self.GUI.update_variable("boxes", self.boxes)
        self.GUI.step()
