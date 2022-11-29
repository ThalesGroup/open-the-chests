import random
from typing import List, Dict


class Pattern:

    def __init__(self,
                 instruction: List[Dict],
                 id: int):
        """
        Pattern associated to a box that uses the defined parser to sample instructions and produce an event stack.
        This structure allows to track the state and execution of situations associated to each box.

        :param instruction: Instruction used to generate the stack of events.
        :param verbose: Print information as it happens.
        """
        self.id = id

        self.timeout = ([command["parameters"]
                         for command in instruction
                         if command["command"] == "delay"] or [0]).pop()

        self.noise = ([command["parameters"]
                       for command in instruction
                       if command["command"] == "noise"] or [0]).pop()

        self.instruction = [instr for instr in instruction if instr["command"] not in ["delay",
                                                                                       "noise"]]
        # used for GUI only to print full patterns
        self.full_pattern = []

    def generate_timeout(self):
        return random.uniform(0, self.timeout)

    def reset(self):
        """
        Reset pattern and all related information.
        """
        self.full_pattern = []

    def get_timeout(self):
        return self.timeout

    def get_noise(self):
        return self.noise
