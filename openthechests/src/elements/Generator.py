import random
from collections import defaultdict
from typing import List, Dict

import numpy as np

from openthechests.openthechests.src.elements.Event import Event
from openthechests.openthechests.src.elements.Parser import Parser
from openthechests.openthechests.src.elements.Pattern import Pattern


class Generator:
    """
    Generates synthetic event sequences from a set of `Pattern` objects using a `Parser`.

    This class orchestrates:
    - Sampling of patterns (structured event instructions)
    - Temporal placement of events in time
    - Injection of noise events
    - Management of "event stacks" per pattern, which represent pending events in the simulation

    It is primarily used inside an environment loop to produce:
    - The **next event** to process
    - Corresponding **signals** indicating pattern state changes (e.g., "active", "satisfied")

    Attributes
    ----------
    parser : Parser
        The parser responsible for instantiating events and adding noise.
        Must implement `instantiate_pattern()` and `make_noise()`.
    patterns : dict[int, Pattern]
        A mapping from pattern IDs to `Pattern` instances.
    verbose : bool
        If True, prints debug output during event generation.
    event_stacks : dict[int, list[Event]]
        Internal storage of pending events per pattern.
        Each value is a list of `Event` objects, sorted by start time.

    Methods
    -------
    reset() -> None
        Clears all event stacks and regenerates them from scratch for each pattern.
    next_event() -> tuple[Event, dict]
        Returns the chronologically earliest event across all patterns
        and updates stacks/signals accordingly.
    disable_timeline(pattern_id: int) -> None
        Removes the event stack for a given pattern ID.
    get_timeline() -> list[Event]
        Returns the first (next) event from each pattern's stack.

    Private Methods
    ---------------
    _generate_noise_events(pattern_noise: float, pattern_end: float, pattern_len: int) -> list[Event]
        Samples noise events according to a binomial distribution and shifts them to before `pattern_end`.
    _fill_event_stack(t: float, pattern: Pattern, last_generated_event: Event | None) -> list[Event]
        Generates all events for a pattern starting from time `t`, including noise,
        and returns them as a sorted event list.
    """

    def __init__(self,
                 parser: Parser,
                 patterns: List[Pattern],
                 verbose: bool = False):
        """
        Initialize the Generator.

        Parameters
        ----------
        parser : Parser
            Responsible for instantiating event objects and generating noise.
        patterns : list[Pattern]
            The set of patterns to generate from.
        verbose : bool, optional
            If True, enable debug printing.
        """
        self.parser: Parser = parser
        self.patterns: Dict[int, Pattern] = {pattern.id: pattern for pattern in patterns}
        self.verbose: bool = verbose
        self.event_stacks = dict()

    def reset(self):
        """
        Resets the event stacks and fills them with generated events based on the patterns.

        This:
        - Clears existing stacks.
        - Calls `pattern.reset()` for each pattern.
        - Fills each stack with a new sequence of events starting from a random
          point in the pattern's timeout window.
        """
        self.event_stacks = dict()
        for pattern in self.patterns.values():
            pattern.reset()
            generated_stack = self._fill_event_stack(pattern)
            self.event_stacks[pattern.id] = generated_stack

    def _generate_noise_events(self, pattern_noise, pattern_end, pattern_len):
        """
        Generates a list of noise events proportional to the number of normal events in the pattern.

        Noise count is drawn from a **binomial distribution** with:
        - n = number of events in the pattern
        - p = pattern noise ratio

        Parameters
        ----------
        pattern_noise : float
            Probability of a noise event for each event in the pattern.
        pattern_end : float
            End time of the pattern (noise events will occur before this).
        pattern_len : int
            Number of events in the pattern.

        Returns
        -------
        list[Event]
            Noise events generated using the parser.
        """

        noise_list = [self.parser.make_noise(before=pattern_end)
                      for _ in range(np.random.binomial(pattern_len, pattern_noise))]
        return noise_list

    def _fill_event_stack(self, pattern, previous_patter_end=0, last_generated_event=None):
        """
        Generates all events for a given pattern, applying a random start-time offset
        from the pattern's timeout distribution.

        Process:
        1. Samples a random start offset via `pattern.sample_timeout()`.
        2. Instantiates the pattern's base events using the parser.
        3. Shifts all generated events by the start offset.
        4. Adds noise events (also shifted).
        5. Updates the pattern's `full_pattern` for visualization/debugging.

        Parameters
        ----------
        pattern : Pattern
            Pattern object containing event generation instructions.
        last_generated_event : Event, optional
            If provided, stored as the first entry in `pattern.full_pattern`.

        Returns
        -------
        list[Event]
            All generated events (pattern + noise), sorted by end time.
        """

        pattern_start = previous_patter_end + pattern.sample_timeout()

        generated_events = self.parser.instantiate_pattern(pattern.instruction)

        pattern_end_time = generated_events[-1].end
        noise_events = self._generate_noise_events(pattern.noise, pattern_end_time, len(generated_events))

        shifted_generated_events = [event.shifted(pattern_start) for event in generated_events]
        shifted_noise_events = [event.shifted(pattern_start) for event in noise_events]

        # keep last event in memory for visualisation purposes
        pattern.full_pattern = [last_generated_event] if last_generated_event else []
        pattern.full_pattern += shifted_generated_events

        events_stack = sorted(shifted_noise_events + shifted_generated_events)
        if self.verbose:
            print(f"Sampling new events from pattern {pattern.id}: {events_stack}")

        return events_stack

    def next_event(self):
        """
        Retrieves the next chronological event across all patterns and updates stacks.

        Also produces **signals** indicating:
        - `"satisfied"`: when a pattern completes its current stack.
        - `"active"`: when the current event overlaps with the start of another pattern's event.

        Returns
        -------
        tuple[Event, dict]
            The earliest event and a signal dictionary where keys are pattern IDs and values
            are lists of signal strings.
        """
        next_event = Event(e_type="Empty", e_attributes={}, t_start=0, t_end=0)
        signal = defaultdict(list)
        pattern_to_sample_id = -1
        if self.event_stacks:
            # uses event 'less than' function to compare event ends
            pattern_to_sample_id = min(self.event_stacks,
                                       key=lambda pattern_id: self.event_stacks[pattern_id][0])
            pattern_to_sample = self.patterns[pattern_to_sample_id]
            next_event = self.event_stacks[pattern_to_sample_id].pop(0)
            signal[pattern_to_sample_id].append("active")
            if not self.event_stacks[pattern_to_sample_id]:
                signal[pattern_to_sample_id].append("satisfied")
                self.event_stacks[pattern_to_sample_id] = self._fill_event_stack(pattern_to_sample,
                                                                                 next_event.end,
                                                                                 next_event)
        for pattern_id, stack in self.event_stacks.items():
            if pattern_id != pattern_to_sample_id:
                if next_event.start >= stack[0].start:
                    signal[pattern_id].append("active")

        return next_event, dict(signal)

    def disable_timeline(self, pattern_id: int):
        """
        Removes the event stack for the given pattern ID.

        Parameters
        ----------
        pattern_id : int
            Pattern ID to remove from the timeline.
        """
        self.event_stacks.pop(pattern_id, None)

    def get_timeline(self):
        """
        Get the **next event** from each pattern's stack.

        Returns
        -------
        list[Event]
            The first event from each pattern's event stack.
        """
        return [event_stack[0] for event_stack in self.event_stacks.values()]
