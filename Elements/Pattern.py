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


class Pattern:

    def __init__(self, instruction: str, verbose):
        self.verbose = verbose
        self.instruction = instruction
        self.instruction_buffer = []
        self.satisfied = False
        self.current_time = 0

    def get_next(self, t):
        event = Event(self.instruction, [0, 0, 0], t, t + random.random() * 5)
        if self.verbose : print(f"Sampling event {self.instruction}", end=" ")
        return event
