import random
from typing import List, Dict

import numpy as np

from openthechests.src.elements.Event import Event
from openthechests.src.elements.Parser import Parser
from openthechests.src.elements.Pattern import Pattern


class Generator:
    """
    A class to generate events based on patterns and a parser.

    Attributes:
    -----------
    parser : Parser
        The parser structure used for sampling events.
    patterns : Dict[int, Pattern]
        A dictionary mapping pattern IDs to their respective Pattern objects.
    verbose : bool
        A flag to enable verbose output for debugging purposes.
    event_stacks : dict
        A dictionary storing event stacks for each pattern.

    Methods:
    --------
    reset():
        Resets the event stacks and fills them with generated events based on patterns.
    next_event():
        Retrieves the next event to be processed and updates the event stacks.
    disable_timeline(pattern_id: int):
        Disables the timeline for a specific pattern by removing its event stack.
    get_timeline():
        Returns the current timeline of events.

    Hidden Methods
    --------------
    _generate_noise_events(pattern_noise, pattern_end, pattern_len):
        Generates a list of noise events proportional to the list of normal events for the pattern.
    _fill_event_stack(t, pattern, last_generated_event=None):
        Fills the pattern stack starting at time t with generated events.
    """

    def __init__(self,
                 parser: Parser,
                 patterns: List[Pattern],
                 verbose: bool = False):
        """
        Initializes the Generator with a parser, patterns, and an optional verbosity flag.

        :param parser: Parser
            The parser structure used for sampling events.
        :param patterns: List[Pattern]
            A list of patterns used to generate events.
        :param verbose: bool, optional
            A flag to enable verbose output for debugging purposes (default is False).
        """
        self.parser: Parser = parser
        self.patterns: Dict[(int, Pattern)] = {pattern.id: pattern for pattern in patterns}
        self.verbose: bool = verbose

        self.event_stacks = dict()

    def reset(self):
        """
        Resets the event stacks and fills them with generated events based on the patterns.
        """
        self.event_stacks = dict()
        for pattern in self.patterns.values():
            pattern.reset()
            generated_stack = self._fill_event_stack(random.uniform(0, pattern.timeout), pattern)
            self.event_stacks[pattern.id] = generated_stack

    def _generate_noise_events(self, pattern_noise, pattern_end, pattern_len):
        """
        Generates a list of noise events proportional to the list of normal events for the pattern.
        Ensures noise events are generated before the pattern end time.

        :param pattern_noise: float
            The noise ratio for the pattern.
        :param pattern_end: float
            The end time of the pattern.
        :param pattern_len: int
            The length of the pattern used to track noise to event ratio.
        :return: List[Event]
            A list of noise events.
        """

        noise_list = [self.parser.make_noise(before=pattern_end)
                      for _ in range(np.random.binomial(pattern_len, pattern_noise))]
        return noise_list

    def _fill_event_stack(self, t, pattern, last_generated_event=None):
        """
        Fills the pattern stack starting at time t with events generated following the pattern's instructions.
        Events are generated using the parser.

        :param t: float
            The start time for generating the pattern.
        :param pattern: Pattern
            The pattern object containing instructions for generating events.
        :param last_generated_event: Event, optional
            The last generated event to start from (default is None).
        :return: List[Event]
            A list of events sorted by time.
        """

        t = t + pattern.sample_timeout()

        generated_events = self.parser.instantiate_pattern(pattern.instruction)

        pattern_end_time = generated_events[-1].end
        shifted_generated_events = [event.shifted(t) for event in generated_events]

        noise_events = self._generate_noise_events(pattern.noise, pattern_end_time, len(generated_events))
        shifted_noise_events = [event.shifted(t) for event in noise_events]

        pattern.full_pattern = [last_generated_event] if last_generated_event else []
        pattern.full_pattern += shifted_generated_events

        events_stack = sorted(shifted_noise_events + shifted_generated_events)
        if self.verbose:
            print(f"Sampling pattern {events_stack}")

        return events_stack

    def next_event(self):
        """
        Retrieves the next event to be processed and updates the event stacks.
        Also generates signals indicating the state of each pattern.

        :return: tuple
            A tuple containing the next event and a signal dictionary.
        """
        next_event = Event(e_type="Empty", e_attributes={}, t_start=0, t_end=0)
        signal = dict()
        if self.event_stacks:
            pattern_to_sample_id = min(self.event_stacks,
                                       key=lambda pattern_id: self.event_stacks[pattern_id][0])
            pattern_to_sample = self.patterns[pattern_to_sample_id]
            next_event = self.event_stacks[pattern_to_sample_id].pop(0)
            if not self.event_stacks[pattern_to_sample_id]:
                signal = {pattern_to_sample_id: ["satisfied", "active"]}
                self.event_stacks[pattern_to_sample_id] = self._fill_event_stack(next_event.end,
                                                                                 pattern_to_sample,
                                                                                 next_event)
        for pattern_id, stack in self.event_stacks.items():
            if pattern_id != pattern_to_sample:
                if next_event.end >= stack[0].start:
                    signal[pattern_id] = signal.get(pattern_id, []) + ["active"]

        return next_event, signal

    def disable_timeline(self, pattern_id: int):
        """
        Disables the timeline for a specific pattern by removing its event stack.

        :param pattern_id: int
            The ID of the pattern to disable.
        """
        self.event_stacks.pop(pattern_id, None)

    def get_timeline(self):
        """
        Returns the current timeline of events.
        Where timeline refers to the next events to be generated.

        :return: List[Event]
            A list of the next events in each pattern's stack.
        """
        return [event_stack[0] for event_stack in self.event_stacks.values()]
