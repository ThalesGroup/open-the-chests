import copy
import random
from typing import List, Dict

from openthechests.src.elements.Event import Event
from openthechests.src.utils import helper_functions
from openthechests.src.utils.allen import allen_relations, allen_functions


class Parser:
    """
    The `Parser` is responsible for **generating events** from a set of available event
    and noise types, attributes, and instructions.

    It can:
    - Convert between human-readable (`Event`) and labelled (integer-indexed) forms.
    - Generate noise events before a given time.
    - Instantiate a full event pattern from an instruction list (including Allen relations).
    - Keep statistics on event durations for sampling.

    Parameters
    ----------
    all_event_types : list of str
        All possible event types for **true events** in the environment.
    all_noise_types : list of str
        All possible event types for **noise events**.
    all_event_attributes : dict of str -> list
        Mapping of event attribute names to possible values for true events.
    all_noise_attributes : dict of str -> list
        Mapping of event attribute names to possible values for noise events.

    Attributes
    ----------
    all_event_types : list of str
        Stored set of event types for true events.
    all_noise_types : list of str
        Stored set of event types for noise events.
    all_event_attributes : dict
        Attributes for event generation.
    all_noise_attributes : dict
        Attributes for noise generation.
    min_max_durations : dict
        Tracks min and max observed durations (used when no duration is given).
    all_types : list
        Combined list of event + noise types (used for label encoding).
    all_attributes : dict
        Combined event + noise attributes (used for label encoding).
    """

    def __init__(self,
                 all_event_types: List[str],
                 all_noise_types: List[str],
                 all_event_attributes: Dict[str, List],
                 all_noise_attributes: Dict[str, List]):
        """
        Initialize a Parser with the full set of allowed event and noise definitions.

        Parameters
        ----------
        all_event_types : list of str
            All possible event types for **true events** in the environment.
        all_noise_types : list of str
            All possible event types for **noise events**.
        all_event_attributes : dict of str -> list
            Mapping of event attribute names to possible values for true events.
        all_noise_attributes : dict of str -> list
            Mapping of event attribute names to possible values for noise events.
        """
        self.all_event_types = all_event_types
        self.all_noise_types = all_noise_types
        self.all_event_attributes = all_event_attributes
        self.all_noise_attributes = all_noise_attributes

        # Used for event generation when no duration is specified
        self.min_max_durations = {"min": 1, "max": 1}

        # Merge all event/noise types and attributes for label encoding
        self.all_types = all_event_types + all_noise_types
        self.all_attributes = copy.deepcopy(all_event_attributes)
        for key, value in all_noise_attributes.items():
            if key in self.all_event_attributes:
                self.all_attributes[key].extend(value)
            else:
                self.all_attributes[key] = value

    def event_to_labelled(self, event: Event) -> Event:
        """
        Convert an event with string type/attributes to a **labelled** version,
        where type and attribute values are replaced with integer indices.

        Events with empty attributes (e.g. from dataset mode) are returned with
        an empty attribute dict — no encoding is attempted.

        Parameters
        ----------
        event : Event
            Original event with string type/attributes.

        Returns
        -------
        Event
            New event with integer-encoded type and attribute values.
        """
        label_e_type = self.all_types.index(event.type)
        label_attributes = {
            key: self.all_attributes[key].index(value)
            for key, value in event.attributes.items()
        }
        return Event(label_e_type, label_attributes, event.start, event.end)

    def labelled_to_event(self, event: Event) -> Event:
        """
        Convert a **labelled** event (integer type/attributes) back to
        its original human-readable form.

        Parameters
        ----------
        event : Event
            Labelled event (integer-coded).

        Returns
        -------
        Event
            New event with decoded type and attribute values.
        """
        e_type = self.all_types[event.type]
        attributes = {
            key: self.all_attributes[key][value]
            for key, value in event.attributes.items()
        }
        return Event(e_type, attributes, event.start, event.end)

    def make_noise(self, before: float) -> Event:
        """
        Generate a **random noise event** ending before a given time.

        Event type and attributes are chosen from noise definitions provided at init.

        Parameters
        ----------
        before : float
            Upper bound for event end time.

        Returns
        -------
        Event
            Noise event with random type, attributes, and start/end times.
        """
        t1, t2 = random.uniform(0, before), random.uniform(0, before)
        start, end = min(t1, t2), max(t1, t2)
        e_type = random.choice(self.all_noise_types)
        attributes = {}
        for attr, attr_values in self.all_noise_attributes.items():
            if attr not in attributes:
                attributes[attr] = random.choice(attr_values)
        return Event(e_type, attributes, start, end)

    def instantiate_pattern(self, pattern) -> List[Event]:
        """
        Generate a list of events from a pattern, branching on its mode.

        **Config mode** (``pattern.instruction_type == "config"``)
            Iterates ``pattern.instruction`` and executes ``"instantiate"``
            and Allen-relation commands to produce events stochastically.

        **Dataset mode** (``pattern.instruction_type == "dataset"``)
            Randomly samples one pre-loaded trace from ``pattern.traces``.
            Records event durations so that noise generation (which uses
            ``_get_random_duration_dist``) has sensible statistics.

        Parameters
        ----------
        pattern : Pattern
            Pattern object carrying either instructions (config) or traces (dataset).

        Returns
        -------
        list of Event
            Events sorted by end time.

        Raises
        ------
        ValueError
            If an unknown command is encountered in config mode.
        """
        if pattern.instruction_type == "dataset":
            trace = random.choice(pattern.traces)
            for event in trace:
                self._record_duration(event.duration)
            return sorted(trace)

        # --- Config mode ---
        variables = dict()
        for instr_line in pattern.instruction:
            if instr_line["command"] == "instantiate":
                event = self._make_event(*instr_line["parameters"])
                variables[instr_line["variable_name"]] = event
            elif instr_line["command"] in allen_relations:
                events = (variables[var_name] for var_name in instr_line["parameters"])
                allen_op = instr_line["command"]
                bonus_params = instr_line["other"] if "other" in instr_line else dict()
                event = allen_functions[allen_op](*events, **bonus_params)
                variables[instr_line["variable_name"]] = event
            else:
                raise ValueError("Unknown allen command: " + str(instr_line["command"]))
        return sorted(variables.values())

    def _make_event(self,
                    e_type: str = None,
                    attributes: dict = None,
                    duration_distribution: dict = None) -> Event:
        """
        Create an event with given type, attributes, and duration distribution.

        If any are not provided, random choices are made from allowed values.

        Parameters
        ----------
        e_type : str, optional
            Event type (must be in `all_event_types` if given).
        attributes : dict, optional
            Mapping of attribute names to values (must match allowed values if given).
        duration_distribution : dict, optional
            Dictionary with 'mu' and 'sigma' for sampling duration
            via truncated normal distribution.

        Returns
        -------
        Event
            Generated event starting at time 0 and lasting the sampled duration.
        """
        if e_type is None:
            e_type = random.choice(self.all_event_types)

        if attributes is None:
            attributes = dict()

        for attr, attr_values in self.all_event_attributes.items():
            if attr not in attributes:
                attributes[attr] = random.choice(attr_values)

        self._check_event_values(e_type=e_type,
                                 attributes=attributes)

        if duration_distribution is not None:
            self._record_duration(duration_distribution["mu"])
        else:
            duration_distribution = self._get_random_duration_dist()
        duration_instance = helper_functions.my_normal(**duration_distribution)

        return Event(e_type, attributes, 0, duration_instance)

    def _check_event_values(self, e_type: str, attributes: dict):
        """
        Validate that event type and attributes are allowed.

        When ``attributes`` is empty (e.g. events from dataset mode that carry
        no symbolic attributes), attribute validation is skipped entirely.

        Parameters
        ----------
        e_type : str or None
            Event type to validate (if not None).
        attributes : dict
            Attribute dictionary to validate.  Pass ``{}`` to skip attribute checks.

        Raises
        ------
        AssertionError
            If type or attributes are invalid.
        """
        assert (e_type is None) or e_type in self.all_event_types, \
            f"Unknown event type {e_type}, please select type from all possible types : {self.all_event_types}"
        if attributes:
            assert all([attr in self.all_event_attributes.keys() for attr in attributes]), \
                f"Unknown attribute key, please select attribute keys from {self.all_event_attributes.keys()}"
            assert all([val in self.all_event_attributes[key] for key, val in attributes.items()]), \
                f"Unknown attribute value, please select values according to keys from {self.all_event_attributes}"

    def _record_duration(self, duration: float):
        """
        Update recorded min/max durations.

        Used when generating events without a specified duration distribution.

        Parameters
        ----------
        duration : float
            Duration to consider for updating min/max.
        """
        self.min_max_durations["min"] = min(duration, self.min_max_durations["min"])
        self.min_max_durations["max"] = max(duration, self.min_max_durations["max"])

    def _get_random_duration_dist(self) -> dict:
        """
        Generate a random duration distribution based on recorded min/max.

        Returns
        -------
        dict
            Dictionary with 'mu' and 'sigma' for a truncated normal distribution.
        """
        sigma = (self.min_max_durations["max"] - self.min_max_durations["min"]) / 2
        mu = self.min_max_durations["min"] + sigma
        return {"mu": mu, "sigma": sigma}
