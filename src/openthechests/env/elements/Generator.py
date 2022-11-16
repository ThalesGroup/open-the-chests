import random


class Generator:
    def __init__(self,
                 verbose,
                 parser,
                 patterns):
        """

        :param verbose:
        :param parser: Parser structure used for sampling.
        :param patterns:
        """
        self.parser = parser
        self.patterns = patterns
        self.verbose = verbose

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

        pattern.events_stack = sorted(shifted_noise_events + shifted_generated_events)

        if self.verbose:
            print(f"Sampling pattern {pattern.events_stack}")

    def get_next(self, pattern_id):
        """
        Get the next event on the stack.
        If @self.event_stack has finished refill it,
        starting at the end of the last observed event from the pattern
        plus the specified timeout.

        :return: The next event on the stack
        """
        pattern = self.patterns[pattern_id]
        if not pattern.events_stack:
            if self.verbose:
                print("Pattern finished generating new one")
            pattern.satisfied = True
            pattern.start_pattern_time = pattern.last_event_end + random.uniform(0, pattern.timeout)
            self.fill_event_stack(pattern.start_pattern_time, pattern)

        next_event = pattern.events_stack.pop(0)
        pattern.last_generated_event = next_event
        pattern.last_event_end = next_event.end
        return next_event

    def reset(self):
        for pattern in self.patterns:
            pattern.reset()
            self.fill_event_stack(random.uniform(0, pattern.timeout), pattern)
