import random
from typing import List, Dict


class Pattern:
    """
    Pattern associated to a box that uses the defined parser to sample instructions and produce an event stack.
    This structure allows tracking the state and execution of situations associated with each box.

    Attributes:
    -----------
    id : int
        The unique identifier of the pattern.
    timeout : float
        The timeout value extracted from the instruction, indicating the delay time for events.
    noise : float
        The noise value extracted from the instruction, indicating the noise level for events.
    instruction : List[Dict]
        The list of instructions to generate the stack of events, excluding 'delay' and 'noise' commands.
    full_pattern : List
        A list used for GUI purposes to print the full pattern of events.

    Methods:
    --------
    sample_timeout():
        Returns a random value uniformly sampled between 0 and the timeout.
    reset():
        Resets the pattern and all related information.
    get_timeout():
        Returns the timeout value of the pattern.
    get_noise():
        Returns the noise value of the pattern.
    """

    def __init__(self,
                 instruction: List[Dict],
                 id: int):
        """
        Initializes a Pattern object with the given instructions and ID.
        This pattern will be used for generating events in the environment.

        :param instruction: List[Dict]
            The list of instructions used to generate the stack of events.
        :param id: int
            The unique identifier of the pattern.
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

    def sample_timeout(self):
        """
        Returns a random value uniformly sampled between 0 and the timeout.

        :return: float
            A random value between 0 and the timeout.
        """
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
