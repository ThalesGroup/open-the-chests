import math
from typing import List

import numpy as np

from Dynamics.GUI import BoxEventGUI
from Dynamics.Parser import Parser
from Elements.Event import Event
from Elements.InteractiveBox import InteractiveBox
from Elements.Pattern import Pattern
from utils.utils import process_obs, bug_print


class Environment:
    def __init__(self,
                 instructions: dict,
                 all_event_types: list,
                 all_event_attributes: dict,
                 verbose: bool,
                 stb3: bool = False):
        """
        Environment that allows to interact and open boxes after observing symbols.

        :param instructions: Dictionary of commands allowing to define patterns for each box
        :param all_event_types: List of all possible event types that can take place
        :param all_event_attributes: Dictionary of al event types with a corresponding list of possible values
        :param verbose: Print details when executing for debugging
        :param stb3: Use environment with stable baselines 3
        """
        self.action = None
        self.context = None
        self.last_action = None
        self.stb3 = stb3
        self.time = 0
        self.verbose = verbose
        self.done = False
        self.num_boxes = len(instructions)

        self.parser = Parser(all_event_types, all_event_attributes)
        self.GUI = BoxEventGUI(self.num_boxes, self.parser.label_to_attr)

        self.patterns = [Pattern(self.parser, instr, self.verbose) for instr in instructions]
        self.timeline = {}

        self.boxes = [InteractiveBox(idx, pattern, self.verbose) for idx, pattern in enumerate(self.patterns)]

        if self.verbose:
            print(f"All event types : {all_event_types}")
            print(f"All event attributes : {all_event_attributes}")
            print(f"Initialising {self.num_boxes} boxes with patterns")

    def reset(self):
        """
        Reset the environment.
        Restart time, reset each box and its pattern and refill the timeline of events.
        Get one observation of the newly reset environment.

        :return: The first observation of the newly reset environment
        """
        if self.verbose:
            print("Starting Reset")
        self.time = 0
        for box in self.boxes:
            box.reset(self.time)
            self.timeline[box.id] = box.pattern.get_next()

        self.internal_step()

        obs = self.get_observations()

        if self.verbose:
            print("Reset Done")

        return obs

    def step(self, action: List[int]):
        """
        Move forward the environment by one step using the selected action.

        :param action: List of box ids to attempt to open
        :return: Reward obtained from acting and context at the end of the environment step
        """

        if self.verbose:
            print("\nStart Step")

        # apply action and collect reward
        reward = self.apply_action(action)

        # advance environment and collect context
        self.internal_step()
        obs = self.get_observations()

        self.done = self.check_end()

        if self.verbose:
            print("Step Done \n")

        # TODO (priority 2) fill info dict? use it somehow?
        return obs, reward, self.done, dict()

    def get_observations(self):
        """
        Return an observation of the elements visible to a player.
        Return contains:
            - State information showing if @self.boxes are active or open
            - Context information showing last observed event
        :return:
        """
        active = []
        open = []

        # TODO (priority 3) this can be optimised
        for box_id in range(self.num_boxes):
            active.append(self.boxes[box_id].is_active())
            open.append(self.boxes[box_id].is_open())

        box_states = {"active": active, "open": open}

        obs = {"state": box_states, "context": self.context}

        # TODO (priority 4) explain and document the need for this step
        if self.stb3:
            obs = process_obs(obs)
        return obs

    def internal_step(self):
        """
        Execute one internal step to advance internal environment state
        :return: context resulting from environment exogenous development
        """
        if self.verbose:
            print("Making one internal step to get context and advance timeline")

        self.advance_timeline()
        self.update_boxes(self.time)

    def advance_timeline(self):
        # TODO (priority 4) doc
        """
        Advance internal environment event activity by one step in order to obtain new observations.
        """

        if self.verbose:
            print(f"Active timeline {self.timeline}")

        ending_box_id = min(self.timeline, key=self.timeline.get)
        self.context = self.timeline[ending_box_id]
        self.time = self.context.end

        # TODO (priority 3) what is the interest of this if? make it clear or move it somewhere
        # if only useful at end when selected box is open since all boxes are open
        if not self.boxes[ending_box_id].is_open():
            event = self.boxes[ending_box_id].pattern.get_next()
            self.timeline[ending_box_id] = event

        if self.verbose:
            print(f"Finding closes end value {self.time}")
            print(f"Advancing time to {self.time}")
            print(f"Sampling from boxes {ending_box_id}")
            print(f"Observing context {self.context}")

    def update_boxes(self, t_current):
        # TODO (priority 4) doc and optimise
        """
        Update all boxes states in coherence with system evolution.

        :param t_current: the current system time used to re-activate boxes if needed.
        """
        for box in self.boxes:
            box.update(t_current)

    def apply_action(self, action):
        """
        Apply given action to system and update environment according to action effects.

        :param action: The action to apply
        :return: Reward obtained for the selected action.
        """
        # TODO (priority 4) doc
        self.action = action
        if self.verbose:
            print(f"Applying action {action}")
        reward = []
        for box_id in range(len(action)):
            if action[box_id] == 1:
                opened = self.boxes[box_id].press_button()
                if opened:
                    self.disable_timeline(box_id)
                reward.append(opened)
        return sum(reward)

    def disable_timeline(self, box_id):
        """
        Disable the timeline for a certain box id.
        :param box_id: The box id to remove from the game.
        """
        # TODO (priority 3) sent this to get_next possibly via box opening? remove event stack to prevent problems?
        self.timeline[box_id] = Event("end", dict(), math.inf, math.inf)

    def check_end(self):
        """
        Verify if all boxes have been opened and thus the end of the game has been reached.
        :return: Boolean indicating the end of the game
        """
        # TODO (priority 4) doc
        return all([box.is_open() for box in self.boxes])

    def render(self):
        self.GUI.add_event_to_history(self.context)
        self.GUI.update_variable("context", self.context)
        self.GUI.update_variable("time", self.time)
        self.GUI.update_variable("last_action", self.action)
        self.GUI.step(self.boxes)
