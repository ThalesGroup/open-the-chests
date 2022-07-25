import copy

class Pattern:

    def __init__(self, parser, instruction: list, verbose):
        """
        Initialise pattern allowing to generate events

        :param instruction: Instruction that generates lists of events
        :param verbose: Print information as it happens
        :param parser: parser to use for generating list of Events from instructions
        """
        self.parser = parser
        # TODO (priority 2) move wait instruction time to parser?or not?
        self.timeout = instruction[0]["parameters"]
        self.instruction = instruction[1:]  # list of instructions under the form of dictionaries
        self.verbose = verbose

        self.events_stack = []  # stack of events to generate with instruction
        self.full_pattern = []
        self.last_generated_event = None
        self.satisfied = False
        self.start_pattern_time = 0
        self.last_event_end = 0

    def fill_event_stack(self, t):
        """
        Fill pattern stack starting at time @t with events generated following @self.instruction.

        :param t: Date of start of the generated pattern
        """

        generated_events = self.parser.generate_pattern(self.instruction)
        # TODO (priority 3) could this be done without a for loop
        for event in generated_events:
            event.start += t
            event.end += t

        self.events_stack = generated_events
        self.full_pattern = copy.deepcopy(generated_events)
        if self.last_generated_event:
            self.full_pattern.insert(0, self.last_generated_event)

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
            self.start_pattern_time = self.last_event_end + self.timeout
            self.fill_event_stack(self.start_pattern_time)

        next_event = self.events_stack.pop(0)
        self.last_generated_event = next_event
        self.last_event_end = next_event.end
        return next_event
