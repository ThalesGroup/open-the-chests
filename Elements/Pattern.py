import random

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
        # TODO generate full pattern at env reset
        self.verbose = verbose
        # suppose to be list of events following each other
        self.instruction = instruction
        self.events_stack = []
        # initialise events stack
        self.reset(0)
        self.satisfied = False
        self.next_sample_time = 0

    def process_instruction(self):
        # TODO create function that generates a list of events using a written events_stack
        pass

    def get_next(self, t):
        event = []
        # is it time to generate event
        if t >= self.next_sample_time:
            # get next event to be generated
            # TODO handle generations of multiple concurrent events
            # TODO handle wait time
            next_event = self.events_stack.pop(0)
            if not self.events_stack:
                # TODO add pattern satisfaction to box
                # If event stack has finished pattern is considered to be satisfied
                self.satisfied = True
            event.append(next_event)
            if self.verbose: print(f"Sampling event {next_event}", end=" ")
        return event

    def reset(self, t):
        # TODO add reset pattern function that re-generates pattern at box activation
        for instr in self.instruction:
            self.events_stack.append(Event(instr.symbol["e_type"], instr.symbol["attr"], instr.start + t, instr.end + t))
