import math
from typing import List

import numpy as np

from Dynamics.Parser import Parser
from Elements.Event import Event
from Elements.InteractiveBox import InteractiveBox
from Elements.Pattern import Pattern
from utils.utils import process_obs


class Environment:
    def __init__(self,
                 instructions,
                 all_event_types,
                 all_event_attributes,
                 verbose,
                 stb3=False):
        """
        Symbolic environment that allows to interact and open boxes

        :param instructions: Instructions with which to create boxes
        :param verbose: Print details when executing for debugging
        """
        self.stb3 = stb3
        self.time = 0
        self.verbose = verbose
        self.num_boxes = len(instructions)

        self.parser = Parser(all_event_types, all_event_attributes)

        # TODO adapt wait to be processed by parser for pattern
        self.patterns = [Pattern(self.parser, instr, self.verbose) for instr in instructions]

        self.boxes: list[InteractiveBox] = [InteractiveBox(i, self.patterns[i], self.verbose) for i in
                                            range(self.num_boxes)]

        if self.verbose:
            print(f"Initialising {self.num_boxes} boxes")

        self.timeline = {}

        self.done = False

    def reset(self):
        """

        """
        self.time = 0
        for box in self.boxes:
            box.reset()
            box.activate()
            box.pattern.reset(self.time)
            self.timeline[box.id] = box.pattern.get_next(self.time)

        obs = self.get_obs()

        return obs

    def get_obs(self):
        context = self.internal_step()
        box_states = self.observe_box_states()
        obs = {"state": box_states, "context": context}
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

        t_current, context = self.observe_context()
        self.update_boxes(t_current)

        if self.verbose:
            print(f"Advancing time to {t_current}")

        self.time = t_current  # advance time to match context end
        return context

    def observe_context(self):
        """

        :return:
        """
        ending_box_id = min(self.timeline, key=self.timeline.get)
        context = self.timeline[ending_box_id]
        t_current = context.end

        if not self.boxes[ending_box_id].is_open():
            event = self.boxes[ending_box_id].pattern.get_next(t_current)
            self.timeline[ending_box_id] = event

        if self.verbose:
            print(f"Active timeline {self.timeline}")
            print(f"Finding closes end value {t_current}")
            print(f"Sampling from boxes {ending_box_id}")
            print(f"Observing context {context}")

        return t_current, context

    def update_boxes(self, t_current):
        """

        :param t_current:
        """
        for box in self.boxes:
            box.update(t_current)

    def observe_box_states(self):
        active = []
        open = []
        for box_id in range(self.num_boxes):
            active.append(self.boxes[box_id].is_active())
            open.append(self.boxes[box_id].is_open())
        return {"active": active, "open": open}

    def step(self, action: List[int]):
        """
        Move forward the environment by one step using the selected action

        :param action: List of box ids to attempt to open
        :return: Reward obtained from acting and context at the end of the environment step
        """

        if self.verbose:
            print("\nStart Step")

        # apply action and collect reward
        reward = self.apply_action(action)

        self.done = self.check_end()

        # advance environment and collect context
        obs = self.get_obs()

        if self.verbose:
            print("Step Done \n")

        return obs, reward, self.done, dict()

    def apply_action(self, action):
        if self.verbose:
            print(f"Applying action {action}")

        reward = []
        for box_id in range(len(action)):
            if action[box_id] == 1:
                opened = self.boxes[box_id].press_button()
                if opened:
                    # TODO sent this to get_next possibly via box opening?
                    self.timeline[box_id] = Event("end", dict(), math.inf, math.inf)
                reward.append(opened)
        return sum(reward)

    def check_end(self):
        # return all([time == math.inf for time in self.current_end_times.values()])
        return all([box.is_open() for box in self.boxes])
