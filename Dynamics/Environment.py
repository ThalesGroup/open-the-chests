from Elements.InteractiveBox import InteractiveBox


class Environment:
    def __init__(self):
        self.time = 0
        self.context = None
        self.boxes: list[InteractiveBox] = None

        self.step()

    def step(self, action: list[int]):
        reward = []
        for box_id in action:
            reward.append(self.boxes[box_id].press_button())

        context = self.internal_step()

        return reward, context

    def internal_step(self):
        # sample each box pattern for new events at current time
        self.update_events_patterns()
        # observe context and advance time to new observation point
        t_current = context = self.context.observe()
        self.time = t_current
        return context

    def update_events_patterns(self):
        new_events = []
        for box in self.boxes:
            # TODO workaround list concatenation
            new_events += box.pattern.get_next(self.current_time)
        self.context.active_events += new_events

