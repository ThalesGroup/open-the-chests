import random
from typing import List, Dict

import numpy as np

from src.openthechests.env.elements.Event import Event
from src.openthechests.env.elements.Parser import Parser
from src.openthechests.env.elements.Pattern import Pattern


class Generator:
    def __init__(self,
                 verbose: bool,
                 parser: Parser,
                 patterns: List[Pattern]):
        """

        :param verbose:
        :param parser: Parser structure used for sampling.
        :param patterns:
        """
        self.parser: Parser = parser
        self.patterns: Dict[(int, Pattern)] = {pattern.id: pattern for pattern in patterns}
        self.verbose: bool = verbose

        self.event_stacks = dict()

    def reset(self):
        self.event_stacks = dict()
        for pattern in self.patterns.values():
            pattern.reset()
            generated_stack = self._fill_event_stack(random.uniform(0, pattern.timeout), pattern)
            self.event_stacks[pattern.id] = generated_stack

    def _generate_noise_events(self, pattern_noise, pattern_end, pattern_len):
        """
        Generate a list of noise events proportional to the list of normal events for the pattern.
        Use the @self.noise proportion to keep track of the ratio.
        We make sure to generate the noise events before the pattern end _time.


        :param pattern_noise:
        :param pattern_end: The end _time of the pattern.
        :param pattern_len: The length of the pattern used to track noise to event ratio.
        :return: A list of noise events.
        """

        noise_list = [self.parser.make_noise(before=pattern_end)
                      for _ in range(np.random.binomial(pattern_len, pattern_noise))]
        return noise_list

    def _fill_event_stack(self, t, pattern, last_generated_event=None):
        """
        Fill pattern stack starting at _time @t with events generated following @self.instruction.
        Events are generated using the @self.parser.

        :param last_generated_event:
        :param pattern:
        :param t: Date of start of the generated pattern
        """

        t = t + pattern.sample_timeout()

        generated_events = self.parser.instantiate_pattern(pattern.instruction)
        num_not_noise = len(generated_events)
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

    # TODO priority 3: figure out to do with generating an event present as next in multiple patterns
    def next_event(self):
        next_event = Event("Empty", {}, 0, 0)
        signal = dict()
        if self.event_stacks:
            pattern_to_sample_id = min(self.event_stacks, key=lambda pattern_id: self.event_stacks[pattern_id][0])
            pattern_to_sample = self.patterns[pattern_to_sample_id]
            next_event = self.event_stacks[pattern_to_sample_id].pop(0)
            if not self.event_stacks[pattern_to_sample_id]:
                signal = {pattern_to_sample_id: ["satisfied"]}
                self.event_stacks[pattern_to_sample_id] = self._fill_event_stack(next_event.end,
                                                                                 pattern_to_sample,
                                                                                 next_event)
        for pattern_id, stack in self.event_stacks.items():
            if next_event.end >= stack[0].start:
                signal[pattern_id] = signal.get(pattern_id, []) + ["active"]

        return next_event, signal

    def disable_timeline(self, pattern_id: int):
        """
        Remove the box_id from the timeline dictionary, disabling its evolution.
        :param pattern_id: The box id to remove from the game.
        """
        self.event_stacks.pop(pattern_id, None)

    def get_timeline(self):
        return [event_stack[0] for event_stack in self.event_stacks.values()]
