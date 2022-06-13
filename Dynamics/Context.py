from Elements.Event import Event


class Context:
    def __init__(self):
        self.active_events: list[Event] = []

    def observe(self):
        assert self.active_events, "Observing an empty environment not possible"
        closest_event = min(self.active_events, key=lambda x: x.start)
        # TODO numpy and optimise if necessary keep it simple for now
        context = [event for event in self.active_events if event.end == closest_event.end]
        self.active_events = [event for event in self.active_events if event.end > closest_event.end]
        return closest_event.end, context

