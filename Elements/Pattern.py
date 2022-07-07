from Dynamics.utils import print_event_list
from Elements.Event import Event



class Pattern:

    def __init__(self, parser, instruction: list, verbose, timeout=0):
        """
        Initialise pattern allowing to generate events

        :param timeout: Time to wait before restarting pattern
        :param instruction: Instruction that generates lists of events
        :param verbose: Print information as it happens
        :param parser: parser to use for generating list of Events from instructions
        """
        # TODO generate full pattern at env reset
        self.parser = parser
        self.timeout = timeout
        self.verbose = verbose

        self.instruction = instruction  # list of instructions under the form of dictionaries
        self.events_stack = []  # stack of events to generate with instruction
        self.satisfied = False
        self.start_pattern_time = 0

    def reset(self, t, timeout=0):
        """
        Reset pattern and generate new stack of events using instruction
        TODO add reset pattern function that re-generates pattern at box activation

        :param timeout:
        :param t: Time of reset used to regenerate event stack
        """

        # self.satisfied = False
        self.fill_event_stack(t + timeout)
        self.start_pattern_time = self.events_stack[0].start

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

        print_event_list(generated_events)
        self.events_stack = generated_events

    def get_next(self, t_current):
        if not self.events_stack:
            print("Pattern finished")
            self.satisfied = True
            self.start_pattern_time = t_current + self.timeout
            self.reset(self.start_pattern_time)

        next_events = [self.events_stack.pop(0)]
        end_time = next_events[0].end
        while self.events_stack and self.events_stack[0].end == end_time:
            next_events.append(self.events_stack.pop(0))
        return end_time, next_events



"""
    def get_next(self, t):
        event = []
        # is it time to generate event
        if t >= self.start_pattern_time:
            # get next event to be generated
            # TODO handle generations of multiple concurrent events
            # TODO handle wait time
            if not self.satisfied:
                next_event = self.events_stack.pop(0)
                event.append(next_event)
                if self.verbose:
                    print(f"Sampling event {next_event}")
                if not self.events_stack:
                    # TODO add pattern satisfaction to box
                    # If event stack has finished pattern is considered to be satisfied
                    self.satisfied = True
        return event
"""
