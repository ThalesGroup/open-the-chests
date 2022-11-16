import random


class Pattern:

    def __init__(self, parser, instruction: list, verbose):
        """
        Pattern associated to a box that uses the defined parser to sample instructions and produce an event stack.
        This structure allows to track the state and execution of situations associated to each box.

        :param instruction: Instruction used to generate the stack of events.
        :param verbose: Print information as it happens.
        :param parser: Parser structure used for sampling.
        """
        self.parser = parser
        self.timeout = ([command["parameters"]
                         for command in instruction
                         if command["command"] == "delay"] or [0]).pop()

        self.noise = ([command["parameters"]
                       for command in instruction
                       if command["command"] == "noise"] or [0]).pop()

        self.instruction = [instr for instr in instruction if instr["command"] not in ["delay",
                                                                                       "noise"]]
        self.verbose = verbose

        # stack of events to generate with instruction
        self.events_stack = []
        # used for GUI only to print full patterns
        self.full_pattern = []
        self.last_generated_event = None
        # show has pattern finished displaying
        self.satisfied = False
        # re-activation time for pattern
        self.start_pattern_time = 0
        self.last_event_end = 0

    def generate_noise_events(self, pattern_end, pattern_len):
        """
        Generate a list of noise events proportional to the list of normal events for the pattern.
        Use the @self.noise proportion to keep track of the ratio.
        We make sure to generate the noise events before the pattern end time.

        :param pattern_end: The end time of the pattern.
        :param pattern_len: The length of the pattern used to track noise to event ratio.
        :return: A list of noise events.
        """
        num_not_noise = pattern_len
        noise_list = []
        while num_not_noise > 0:
            if random.random() < self.noise:
                noise_event = self.parser.make_noise(before=pattern_end)
                noise_list.append(noise_event)
            else:
                num_not_noise -= 1
        return noise_list

    def reset(self):
        """
        Reset pattern and all related information.
        """
        self.events_stack = []  # stack of events to generate with instruction
        self.full_pattern = []
        self.last_generated_event = None
        self.satisfied = False
        self.start_pattern_time = 0
        self.last_event_end = 0
        self.fill_event_stack(random.uniform(0, self.timeout))

    def fill_event_stack(self, t):
        """
        Fill pattern stack starting at time @t with events generated following @self.instruction.
        Events are generated using the @self.parser.

        :param t: Date of start of the generated pattern
        """

        generated_events = self.parser.generate_pattern(self.instruction)
        num_not_noise = len(generated_events)
        pattern_end_time = generated_events[-1].end
        shifted_generated_events = [event.shifted(t) for event in generated_events]

        noise_events = self.generate_noise_events(pattern_end_time, num_not_noise)
        shifted_noise_events = [event.shifted(t) for event in noise_events]

        self.full_pattern = [self.last_generated_event] if self.last_generated_event else []
        self.full_pattern += shifted_generated_events

        self.events_stack = sorted(shifted_noise_events + shifted_generated_events)

        if self.verbose:
            print(f"Sampling pattern {self.events_stack}")

    def get_next(self):
        """
        Get the next event on the stack.
        If @self.event_stack has finished refill it,
        starting at the end of the last observed event from the pattern
        plus the specified timeout.

        :return: The next event on the stack
        """
        if not self.events_stack:
            if self.verbose:
                print("Pattern finished generating new one")
            self.satisfied = True
            self.start_pattern_time = self.last_event_end + random.uniform(0, self.timeout)
            self.fill_event_stack(self.start_pattern_time)

        next_event = self.events_stack.pop(0)
        self.last_generated_event = next_event
        self.last_event_end = next_event.end
        return next_event
