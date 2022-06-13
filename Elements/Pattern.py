from Elements.Event import Event


def parse_instruction():
    symbol = ("A", [0, 1, 2])
    duration = 2
    return [(symbol, duration)]


class Pattern:

    def __init__(self, instruction: list[tuple]):
        self.instruction = instruction
        self.instruction_buffer = []
        self.satisfied = False

    def sample(self):
        current_instruction = self.instruction.pop(0)
        self.instruction_buffer.append(current_instruction)
        if self.instruction_buffer:
            self.satisfied = True
            self.instruction = self.instruction_buffer
        return current_instruction

