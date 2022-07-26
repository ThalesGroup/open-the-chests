import copy
import random

from utils.utils import bug_print


class Pattern:

    def __init__(self, parser, instruction: list, verbose):
        """
        Initialise pattern allowing to generate events

        :param instruction: Instruction that generates lists of events
        :param verbose: Print information as it happens
        :param parser: parser to use for generating list of Events from instructions
        """
        self.parser = parser
        # TODO (priority 3) move wait instruction time to parser?or not?
        self.timeout = next(filter(lambda instr: instr['command'] == 'delay', instruction))["parameters"]
        # TODO (priority 3) allow not adding noise and it replaced by 0
        self.noise = next(filter(lambda instr: instr['command'] == 'noise', instruction))["parameters"]

        self.instruction = [instr for instr in instruction if instr["command"] not in ["delay",
                                                                                       "noise"]]  # list of instructions under the form of dictionaries
        self.verbose = verbose

        self.events_stack = []  # stack of events to generate with instruction
        self.full_pattern = []
        self.last_generated_event = None
        self.satisfied = False
        self.start_pattern_time = 0
        self.last_event_end = 0

    def generate_noise_events(self, pattern_end, pattern_len):
        num_not_noise = pattern_len
        noise_list = []
        while num_not_noise > 0:
            if random.random() <= self.noise:
                noise_event = self.parser.noise(before=pattern_end)
                noise_list.append(noise_event)
            else:
                num_not_noise -= 1
        return noise_list

    def fill_event_stack(self, t):
        """
        Fill pattern stack starting at time @t with events generated following @self.instruction.

        :param t: Date of start of the generated pattern
        """

        # TODO (priority 1) this code can be prettier
        generated_events = self.parser.generate_pattern(self.instruction)
        num_not_noise = len(generated_events)
        pattern_end = generated_events[-1].end
        noise_events = self.generate_noise_events(pattern_end, num_not_noise)

        self.full_pattern = [self.last_generated_event] if self.last_generated_event else []
        self.full_pattern += [event.shift(t) for event in generated_events]

        self.events_stack = [event.shift(t) for event in sorted(noise_events + generated_events)]

        if self.verbose:
            print(f"Sampling pattern {self.events_stack}")

    def get_next(self):
        """
        Get the next event on the stack.
        If @self.event_stack has finished refill it,
        starting at the end of the last observed event from the pattern
        plus the specified timeout.

        :return: The next event on the stack
        """
        if not self.events_stack:
            if self.verbose:
                print("Pattern finished generating new one")
            self.satisfied = True
            self.start_pattern_time = self.last_event_end + self.timeout
            self.fill_event_stack(self.start_pattern_time)

        next_event = self.events_stack.pop(0)
        self.last_generated_event = next_event
        self.last_event_end = next_event.end
        return next_event
