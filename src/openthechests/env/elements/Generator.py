import random

from src.openthechests.env.elements.Event import Event


class Generator:
    def __init__(self,
                 verbose,
                 parser,
                 patterns: list):
        """

        :param verbose:
        :param parser: Parser structure used for sampling.
        :param patterns:
        """
        self.parser = parser
        self.patterns = patterns
        self.verbose = verbose

        self.timeline = {}
        self.event_stacks = []

    def reset(self):
        self.timeline = {}
        self.event_stacks = []
        for pattern in self.patterns:
            pattern.reset()
            generated_stack = self.fill_event_stack(random.uniform(0, pattern.timeout), pattern)
            self.event_stacks.append(generated_stack)
            next_event = self.get_next_from_stack(pattern.id)
            self.timeline[pattern.id] = next_event

    def generate_noise_events(self, pattern_noise, pattern_end, pattern_len):
        """
        Generate a list of noise events proportional to the list of normal events for the pattern.
        Use the @self.noise proportion to keep track of the ratio.
        We make sure to generate the noise events before the pattern end time.


        :param pattern_noise:
        :param pattern_end: The end time of the pattern.
        :param pattern_len: The length of the pattern used to track noise to event ratio.
        :return: A list of noise events.
        """
        num_not_noise = pattern_len
        noise_list = []
        while num_not_noise > 0:
            if random.random() < pattern_noise:
                noise_event = self.parser.make_noise(before=pattern_end)
                noise_list.append(noise_event)
            else:
                num_not_noise -= 1
        return noise_list

    def fill_event_stack(self, t, pattern):
        """
        Fill pattern stack starting at time @t with events generated following @self.instruction.
        Events are generated using the @self.parser.

        :param pattern:
        :param t: Date of start of the generated pattern
        """

        generated_events = self.parser.generate_pattern(pattern.instruction)
        num_not_noise = len(generated_events)
        pattern_end_time = generated_events[-1].end
        shifted_generated_events = [event.shifted(t) for event in generated_events]

        noise_events = self.generate_noise_events(pattern.noise, pattern_end_time, num_not_noise)
        shifted_noise_events = [event.shifted(t) for event in noise_events]

        pattern.full_pattern = [pattern.last_generated_event] if pattern.last_generated_event else []
        pattern.full_pattern += shifted_generated_events

        events_stack = sorted(shifted_noise_events + shifted_generated_events)
        if self.verbose:
            print(f"Sampling pattern {events_stack}")

        return events_stack

    def get_next_from_stack(self, pattern_id):
        """
        Get the next event on the stack.
        If @self.event_stack has finished refill it,
        starting at the end of the last observed event from the pattern
        plus the specified timeout.

        :return: The next event on the stack
        """
        pattern = self.patterns[pattern_id]
        if not self.event_stacks[pattern_id]:
            if self.verbose:
                print("Pattern finished generating new one")
            pattern.satisfied = True
            pattern.start_pattern_time = pattern.last_event_end + random.uniform(0, pattern.timeout)
            self.event_stacks[pattern_id] = self.fill_event_stack(pattern.start_pattern_time, pattern)

        next_event = self.event_stacks[pattern_id].pop(0)
        pattern.last_generated_event = next_event
        pattern.last_event_end = next_event.end

        return next_event

    def next_event(self):
        res = Event("Empty", {}, 0, 0)
        if self.timeline:
            ending_box_id = min(self.timeline, key=self.timeline.get)
            res = self.timeline[ending_box_id]
            all_satisfied_boxes = [box_id for box_id in self.timeline if self.timeline[box_id] == res]
            for satisfied_box_id in all_satisfied_boxes:
                event = self.get_next_from_stack(satisfied_box_id)
                self.timeline[satisfied_box_id] = event
            if self.verbose:
                print(f"Sampling from boxes {ending_box_id}")
        else:
            if self.verbose:
                print("Timeline is empty as all boxes are opened")
        return res

    def disable_timeline(self, box_id):
        """
        Remove the box_id from the timeline dictionary, disabling its evolution.
        :param box_id: The box id to remove from the game.
        """
        # TODO (priority 3) sent this to get_next possibly via box opening? remove event stack to prevent problems?
        self.timeline.pop(box_id, None)

    def get_timeline(self):
        return self.timeline

