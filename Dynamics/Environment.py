import math
from typing import List

from Dynamics.Parser import Parser
from Elements.InteractiveBox import InteractiveBox
from Elements.Pattern import Pattern


class Environment:
    def __init__(self, instructions: list, all_event_types, all_event_attributes,verbose):
        """
        Symbolic environment that allows to interact and open boxes

        :param instructions: Instructions with which to create boxes
        :param verbose: Print details when executing for debugging
        """
        self.time = 0
        self.verbose = verbose

        self.parser = Parser(all_event_types, all_event_attributes)
        # TODO adapt wait to be processed by parser for pattern
        self.patterns = [Pattern(self.parser, instr[1:], True, instr[0]["parameters"]) for instr in instructions]
        # make one box per pattern
        num_boxes = len(instructions)
        self.boxes: list[InteractiveBox] = [InteractiveBox(i, self.patterns[i]) for i in range(num_boxes)]

        if self.verbose:
            print(f"Initialising {num_boxes} boxes")

        # create context
        self.timeline = {}
        self.current_end_times = {}

        # TODO move to reset function to fit with gym code
        self.done = False

    def reset(self):
        """

        """
        self.time = 0
        for box in self.boxes:
            box.activate()
            box.pattern.reset(self.time)
            end, events = box.pattern.get_next(self.time)
            self.timeline[box.id] = events
            self.current_end_times[box.id] = end
        # make one step to generate new events
        return self.internal_step()

    def internal_step(self):
        """
        Execute one internal step to advance internal environment state
        :return: context resulting from environment exogenous development
        """
        if self.verbose:
            print("Making one internal step to get context and advance timeline")

        # update each pattern and add developments to context
        # self.update_events_patterns()
        # observe context and get new time of context end
        t_current, context = self.observe_context()
        self.update_boxes(t_current)

        if self.verbose:
            print(f"Advancing time to {t_current}")

        # advance time to match context end
        self.time = t_current
        return context

    def observe_context(self):
        min_end_time = min(self.current_end_times.values())
        ending_boxes_ids = [box_id for box_id in self.current_end_times.keys()
                            if self.current_end_times[box_id] == min_end_time]
        # TODO does this really make sense to check if the box is active
        t_current = min_end_time
        if self.verbose:
            print(f"Active timeline {self.timeline}")
            print(f"Next event starts {self.current_end_times}")
            print(f"Finding closes end value {t_current}")
            print(f"Sampling from boxes {ending_boxes_ids}")

        context = []
        for box_id in ending_boxes_ids:
            context += self.timeline[box_id]
            end, event = self.boxes[box_id].pattern.get_next(t_current)
            self.current_end_times[box_id] = end
            self.timeline[box_id] = event

        print(f"Observing context {context}")

        return t_current, context

    def update_boxes(self, t):
        for box in self.boxes:
            box.update(t)

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
        context = self.internal_step()

        if self.verbose:
            print("Step Done \n")

        return reward, context, self.done

    def apply_action(self, action):
        reward = []
        if self.verbose:
            print(f"Applying action {action}")
        for box_id in range(len(action)):
            if action[box_id] == 1:
                opened = self.boxes[box_id].press_button()
                if opened:
                    self.current_end_times[box_id] = math.inf
                    self.timeline[box_id] = [42]
                reward.append(opened)
        return reward

    def check_end(self):
        return all([time == math.inf for time in self.current_end_times.values()])
