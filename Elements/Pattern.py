import math

from Elements.Event import Event


def parse_instruction():
    """
    Return a list of instructions from human written string
    :return: list of machine understandable instructions that allows creation of events
    """
    symbol = ("A", [0, 1, 2])
    duration = 2
    return [(symbol, duration)]


def instructions_to_events(current_instruction, t):
    events = []
    for instr in current_instruction:
        events.append(Event(instr[0][0], instr[0][1], t, t + instr[1][0]))
    return events


"""
Currently event is sampled once previous has ended
In the future event list according to pattern will be pre-generated
"""


class Pattern:

    def __init__(self, instruction: list, verbose):
        """
        Initialise pattern allowing to generate events

        :param instruction: Instruction that generates lists of events
        :param verbose: Print information as it happens
        """
        # TODO generate full pattern at env reset
        self.verbose = verbose

        self.instruction = instruction  # suppose to be list of events for now
        self.events_stack = []  # stack of events to generate with instruction
        # TODO move to environment initialisation
        # self.reset(0)  # reset to fill stack
        self.satisfied = False
        self.next_sample_time = 0

    def reset(self, t):
        """
        Reset pattern and generate new stack of events using instruction
        TODO add reset pattern function that re-generates pattern at box activation

        :param t: Time of reset used to regenerate event stack
        """
        self.fill_event_stack(t)
        self.satisfied = False
        self.next_sample_time = self.events_stack[0].start

        if self.verbose:
            print(f"Sampling pattern {self.events_stack}")

    def fill_event_stack(self, t):
        """
        Transform instruction into list of events
        """
        for instr in self.instruction:
            self.events_stack.append(
                Event(instr.symbol["e_type"], instr.symbol["attr"], instr.start + t, instr.end + t))

    def get_next(self):
        if self.events_stack:
            next_events = [self.events_stack.pop(0)]
            end_time = next_events[0].end
            while self.events_stack and self.events_stack[0].end == end_time:
                next_events.append(self.events_stack.pop(0))
            return end_time, next_events
        else:
            print("Pattern finished")
            self.satisfied = True
            return math.inf, []


"""
    def get_next(self, t):
        event = []
        # is it time to generate event
        if t >= self.next_sample_time:
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