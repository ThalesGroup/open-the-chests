import random


class Pattern:

    def __init__(self, instruction: list, verbose):
        """
        Pattern associated to a box that uses the defined parser to sample instructions and produce an event stack.
        This structure allows to track the state and execution of situations associated to each box.

        :param instruction: Instruction used to generate the stack of events.
        :param verbose: Print information as it happens.
        """
        self.timeout = ([command["parameters"]
                         for command in instruction
                         if command["command"] == "delay"] or [0]).pop()

        self.noise = ([command["parameters"]
                       for command in instruction
                       if command["command"] == "noise"] or [0]).pop()

        self.instruction = [instr for instr in instruction if instr["command"] not in ["delay",
                                                                                       "noise"]]
        self.verbose = verbose
        self.satisfied = False
        self.active = False

        self.events_stack = []
        # used for GUI only to print full patterns
        self.full_pattern = []
        self.last_generated_event = None
        self.start_pattern_time = 0
        self.last_event_end = 0

    def reset(self):
        """
        Reset pattern and all related information.
        """
        self.events_stack = []  # stack of events to generate with instruction
        self.full_pattern = []
        self.last_generated_event = None
        self.satisfied = False
        self.start_pattern_time = 0
        self.last_event_end = 0
