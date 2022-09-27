import random

from src.env.elements.Event import Event

# TODO (priority 4) doc
# TODO (priority 3) rethink class structure and use input all items to generate dictionaries
# TODO (priority 3) rethink labelisation
# TODO (priority 2) add more allen functions
# TODO (priority 2) add check for noise events and noise generation
from src.utils.allen import allen_functions
from src.utils.helper_functions import my_normal


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
        It also allows to labelise events, generate noise events when needed, keep statistics on events lengths.

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
        if all_noise_attributes:
            self.all_attributes = {key: all_noise_attributes[key] + all_event_attributes[key]
                                   for key in all_event_attributes}
        else:
            self.all_attributes = all_event_attributes

    def labelise(self, e_type: str, attributes: dict):
        """
        Transform an event type and a dictionary of attribute values into
        an integer label for the type and a dictionary of attributes with integer label values.

        :param e_type: The event type to be transformed into an integer label.
        :param attributes: The dictionary of attributes to transform. Each value becomes an integer label while parameter names stay unchanged.
        :return: Integer label type and dictionary of attributes with integer label values.
        """
        e_type = self.all_types.index(e_type)
        attributes = {key: self.all_attributes[key].index(value) for key, value in attributes.items()}
        return e_type, attributes

    def make_noise(self, before):
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
        noise = self.instantiate_with_labels(e_type, attributes, start, end)
        return noise

    # TODO (priority 3) add function to check if values are correct
    def make_event(self, e_type: str = None, attributes: dict = {}, duration_distribution: dict() = {}):
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
        assert (e_type is None) or e_type in self.all_event_types, \
            f"Unknown event type {e_type}, please select type from all possible types : {self.all_event_types}"
        assert all([attr in self.all_event_attributes.keys() for attr in attributes]), \
            f"Unknown attribute key, please select attribute keys from {self.all_event_attributes.keys()}"
        assert all([val in self.all_event_attributes[key] for key,val in attributes.items()]), \
            f"Unknown attribute value, please select values according to keys from {self.all_event_attributes}"

        if e_type is None:
            e_type = random.choice(self.all_event_types)
        for attr, attr_values in self.all_event_attributes.items():
            if attr not in attributes:
                attributes[attr] = random.choice(attr_values)

        if duration_distribution:
            self._record_duration(duration_distribution["mu"])
        else:
            duration_distribution = self.get_random_duration_dist()

        duration_inst = my_normal(**duration_distribution)
        event = self.instantiate_with_labels(e_type, attributes, 0, duration_inst)
        return event

    def instantiate_with_labels(self, e_type, attributes, start, end):
        """
        Transform type and attributes to labels and instantiate Event object.

        :param e_type: the type of the event/noise
        :param attributes: the attributes
        :param start: the beginning of the event
        :param end: the end of the event
        :return: an event object with the given information transformed into labels
        """
        e_type, attributes = self.labelise(e_type, attributes)
        noise = Event(e_type, attributes, start, end)
        return noise

    def _record_duration(self, duration):
        """
        Update the records of smallest observed and largest observed durations.
        This is used for generating events that have no specified duration.

        :param duration: The duration to update the values with.
        """
        self.min_max_durations["min"] = min(duration, self.min_max_durations["min"])
        self.min_max_durations["max"] = max(duration, self.min_max_durations["max"])

    # TODO (priority 2) this can be done better
    def get_random_duration_dist(self):
        """
        Get a random duration distribution based on the saved statistics.

        :return: A dictionary giving the mu and sigma of the new distributions
        """
        sigma = (self.min_max_durations["max"] - self.min_max_durations["min"]) / 2
        mu = self.min_max_durations["min"] + sigma
        return {"mu": mu, "sigma": sigma}

    def generate_pattern(self, instructions: dict):
        """
        Generated a pattern of events using a dictionary of commands following a particular format.
        To see exact format refer to examples.instructions.

        :param instructions: The dictionary of commands.
        :return: A list of events that follows the selected instructions.
        """
        event_list = []
        variables = dict()
        for instr_line in instructions:
            if instr_line["command"] == "instantiate":
                event = self.make_event(*instr_line["parameters"])
                variables[instr_line["variable_name"]] = event
                if not event_list:
                    event_list.append(event)
            elif instr_line["command"] in allen_functions.keys():
                events = (variables[var_name] for var_name in instr_line["parameters"])
                allen_op = instr_line["command"]
                bonus_params = instr_line["other"] if "other" in instr_line else dict()
                event = allen_functions[allen_op](*events, **bonus_params)
                variables[instr_line["variable_name"]] = event
                event_list.append(event)
            else:
                # TODO (priority 1) add more errors and tests for correctly used values
                raise ValueError("Unknown allen command: " + str(instr_line["command"]))
        return sorted(variables.values())
