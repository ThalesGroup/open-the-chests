from utils.utils import print_event_list


class Pattern:

    def __init__(self, parser, instruction: list, verbose):
        """
        Initialise pattern allowing to generate events

        :param instruction: Instruction that generates lists of events
        :param verbose: Print information as it happens
        :param parser: parser to use for generating list of Events from instructions
        """
        # TODO generate full pattern at env reset
        self.parser = parser
        self.timeout = instruction[0]["parameters"]
        self.instruction = instruction[1:]  # list of instructions under the form of dictionaries
        self.verbose = verbose

        self.events_stack = []  # stack of events to generate with instruction
        self.satisfied = False
        self.start_pattern_time = 0

    def reset(self, t):
        """
        Reset pattern and generate new stack of events using instruction

        :param t: Time of reset used to regenerate event stack
        """

        # TODO merge two functions no point of having just one ?
        self.fill_event_stack(t)

        if self.verbose:
            print(f"Sampling pattern {self.events_stack}")

    def fill_event_stack(self, t):
        """
        Transform instruction into list of events
        """
        generated_events = self.parser.generate_pattern(self.instruction)
        for event in generated_events:
            event.start += t
            event.end += t

        if self.verbose:
            print_event_list(generated_events)
        self.events_stack = generated_events

    def get_next(self, t_current):
        if not self.events_stack:
            if self.verbose:
                print("Pattern finished")
            self.satisfied = True
            self.start_pattern_time = t_current + self.timeout
            self.reset(self.start_pattern_time)

        next_event = self.events_stack.pop(0)
        return next_event
