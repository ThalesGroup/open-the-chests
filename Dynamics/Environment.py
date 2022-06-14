from typing import List

from Dynamics.Context import Context
from Elements.InteractiveBox import InteractiveBox


class Environment:
    def __init__(self, patterns: list, verbose):
        self.time = 0
        self.verbose = verbose
        # make one box per pattern
        num_boxes = len(patterns)
        if self.verbose: print(f"Initialising {num_boxes} boxes")
        self.boxes: list[InteractiveBox] = [InteractiveBox(i, patterns[i])for i in range(num_boxes)]
        # create context
        self.context = Context(True)
        # make one step to generate new events
        self.internal_step()

    def step(self, action: List[int]):
        reward = []
        for box_id in action:
            reward.append(self.boxes[box_id].press_button())

        context = self.internal_step()

        if self.verbose: print("Step Done \n")
        return reward, context

    def internal_step(self):
        if self.verbose: print("Making one internal step to generate events")
        # sample each box pattern for new events at current time
        self.update_events_patterns()
        # observe context and advance time to new observation point
        t_current, context = self.context.observe()
        if self.verbose: print(f"Advancing time to {t_current}")
        self.time = t_current
        return context

    def update_events_patterns(self):
        if self.verbose: print("Sampling patterns")
        new_events = []
        for box in self.boxes:
            # TODO workaround list concatenation
            new_events += box.pattern.get_next(self.time)
        self.context.active_events += new_events
        if self.verbose: print(f"\nFinished Sampling {self.context.active_events}")

