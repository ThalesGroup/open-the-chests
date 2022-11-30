import copy
import random
from typing import List

from src.openthechests.env.elements.Event import Event
from src.openthechests.env.utils import helper_functions
from src.openthechests.env.utils.allen import allen_functions


class Parser:

    def __init__(self,
                 all_event_types,
                 all_noise_types,
                 all_event_attributes,
                 all_noise_attributes):
        """
        This structure is used for event generation.
        It is defined using the set of all preexistent types and attributes.
        Is main goal is the sampling of events on the basis of instructions.
        It also allows to _labelise events, generate noise events when needed, keep statistics on events lengths.

        :param all_event_types: List of all possible event types to be used for event generation
        :param all_event_attributes: Dictionary of all attributes and their associated possible values
                                                                                for event generation
        :param all_noise_types: List of all possible event types to be used for noise generation
        :param all_noise_attributes: Dictionary of attributes used for noise generation
        """
        self.all_event_types = all_event_types
        self.all_noise_types = all_noise_types
        self.all_event_attributes = all_event_attributes
        self.all_noise_attributes = all_noise_attributes
        # to be used for event generation when no duration is specified
        self.min_max_durations = {"min": 1, "max": 1}

        self.all_types = all_event_types + all_noise_types
        self.all_attributes = copy.deepcopy(all_event_attributes)

        for key, value in all_noise_attributes.items():
            if key in self.all_event_attributes:
                self.all_attributes[key].extend(value)
            else:
                self.all_attributes[key] = value

    def event_to_labelled(self, event: Event) -> Event:
        label_e_type = self.all_types.index(event.type)
        label_attributes = {key: self.all_attributes[key].index(value) for key, value in event.attributes.items()}
        return Event(label_e_type, label_attributes, event.start, event.end)

    def labelled_to_event(self, event: Event) -> Event:
        e_type = self.all_types[event.type]
        attributes = {key: self.all_attributes[key][value] for key, value in event.attributes.items()}
        return Event(e_type, attributes, event.start, event.end)

    def make_noise(self, before: float) -> Event:
        """
        Generate a random noise event ending before a certain date.
        The types and attributes of this event are taken from the sets given at class initialisation

        :param before: Time before which the noise should be generated.
        :return: The defined noise event.
        """
        t1, t2 = random.uniform(0, before), random.uniform(0, before)
        start, end = min(t1, t2), max(t1, t2)
        e_type = random.choice(self.all_noise_types)
        attributes = dict()
        for attr, attr_values in self.all_noise_attributes.items():
            if attr not in attributes:
                attributes[attr] = random.choice(attr_values)
        return Event(e_type, attributes, start, end)

    def instantiate_pattern(self, instructions: List[dict]) -> List[Event]:
        """
        Generated a pattern of events using a dictionary of commands following a particular format.
        To see exact format refer to examples.instructions.

        :param instructions: The dictionary of commands.
        :return: A list of events that follows the selected instructions.
        """
        variables = dict()
        for instr_line in instructions:
            if instr_line["command"] == "instantiate":
                event = self._make_event(*instr_line["parameters"])
                variables[instr_line["variable_name"]] = event
            elif instr_line["command"] in allen_functions.keys():
                events = (variables[var_name] for var_name in instr_line["parameters"])
                allen_op = instr_line["command"]
                bonus_params = instr_line["other"] if "other" in instr_line else dict()
                event = allen_functions[allen_op](*events, **bonus_params)
                variables[instr_line["variable_name"]] = event
            else:
                raise ValueError("Unknown allen command: " + str(instr_line["command"]))
        return sorted(variables.values())

    def _make_event(self, e_type: str = None,
                    attributes: dict = None,
                    duration_distribution: dict = None) -> Event:
        """
        Instantiates an event of given parameters of duration drawn according to a truncated normal distribution.
        If event parameters or type are not specified they are randomly drawn from the list of available ones.

        :param e_type: The type of the event. Eiter None or value belonging to @self.all_event_types.
        :param attributes: Dictionary of attributes.
                            Either empty or filled with values corresponding to @all_event_attributes.
        :param duration_distribution: A tuple (mu, sigma) used to draw a random duration
                            for the event using a truncated normal distribution.
        :return: An event with the selected type, attributes and duration.
        """
        self._check_event_values(e_type=e_type,
                                 attributes=attributes)
        if e_type is None:
            e_type = random.choice(self.all_event_types)

        if attributes is None:
            attributes = dict()
        for attr, attr_values in self.all_event_attributes.items():
            if attr not in attributes:
                attributes[attr] = random.choice(attr_values)

        if duration_distribution is not None:
            self._record_duration(duration_distribution["mu"])
        else:
            duration_distribution = self._get_random_duration_dist()
        duration_instance = helper_functions.my_normal(**duration_distribution)

        return Event(e_type, attributes, 0, duration_instance)

    def _check_event_values(self, e_type: str, attributes: dict):
        assert (e_type is None) or e_type in self.all_event_types, \
            f"Unknown event type {e_type}, please select type from all possible types : {self.all_event_types}"
        assert all([attr in self.all_event_attributes.keys() for attr in attributes]), \
            f"Unknown attribute key, please select attribute keys from {self.all_event_attributes.keys()}"
        assert all([val in self.all_event_attributes[key] for key, val in attributes.items()]), \
            f"Unknown attribute value, please select values according to keys from {self.all_event_attributes}"

    def _record_duration(self, duration):
        """
        Update the records of smallest observed and largest observed durations.
        This is used for generating events that have no specified duration.

        :param duration: The duration to update the values with.
        """
        self.min_max_durations["min"] = min(duration, self.min_max_durations["min"])
        self.min_max_durations["max"] = max(duration, self.min_max_durations["max"])

    def _get_random_duration_dist(self) -> dict:
        """
        Get a random duration distribution based on the saved statistics.

        :return: A dictionary giving the mu and sigma of the new distributions
        """
        sigma = (self.min_max_durations["max"] - self.min_max_durations["min"]) / 2
        mu = self.min_max_durations["min"] + sigma
        return {"mu": mu, "sigma": sigma}
