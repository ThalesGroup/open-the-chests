from Elements.Event import Event


def parse_instruction():
    """
    Return a list of instructions from human written string
    :return: list of machine understandable instructions that allows creation of events
    """
    symbol = ("A", [0, 1, 2])
    duration = 2
    return [(symbol, duration)]


def instruction_to_events(current_instruction, t):
    events = []
    for instr in current_instruction:
        events.append(Event(instr[0][0], instr[0][1], t, t + instr[1][0]))
    return events


class Pattern:

    def __init__(self, instruction: list[tuple]):
        self.instruction = instruction
        self.instruction_buffer = []
        self.satisfied = False
        self.current_time = 0

    def get_next(self, t):
        current_instruction = self.instruction.pop(0)
        self.instruction_buffer.append(current_instruction)
        if self.instruction_buffer:
            self.satisfied = True
            self.instruction = self.instruction_buffer
        current_events = instruction_to_events(current_instruction, t)
        return current_events
