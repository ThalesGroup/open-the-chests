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

    def __init__(self, instruction: str, verbose):
        # TODO generate full pattern at env reset
        # TODO add reset pattern function that re-generates pattern at box activation
        self.verbose = verbose
        self.instruction = instruction
        self.instruction_buffer = []
        self.satisfied = False
        self.next_sample_time = 0

    def get_next(self, t):
        # TODO possible to add multiple events
        event = []
        if t >= self.next_sample_time:
            t = min(t, self.next_sample_time)
            event_time = t + random.random() * 5
            self.next_sample_time = event_time
            event.append(Event(self.instruction, [0, 0, 0], t, event_time))
            if self.verbose: print(f"Sampling event {self.instruction}", end=" ")
        return event
