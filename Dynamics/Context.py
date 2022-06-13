from Elements.Event import Event


class Context:
    def __init__(self):
        self.active_events: list[Event] = []

    def observe(self):
        context = []
        if self.active_events:
            closest_event_end = min(self.active_events, key=lambda x: x.start)
            # TODO numpy and optimise if necessary keep it simple for now
            context = [event for event in self.active_events if event.end == closest_event_end]
            self.active_events = [event for event in self.active_events if event.end > closest_event_end]
        return closest_event_end, context

