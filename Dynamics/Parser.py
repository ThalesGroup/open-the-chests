import random

from utils.allen import allen_functions
from Elements.Event import Event

# TODO (priority 4) doc
# TODO (priority 3) rethink class structure and use input all items to generate dictionaries
# TODO (priority 3) rethink labelisation
# TODO (priority 2) add more allen functions
from utils.utils import list_to_labels, my_normal, bug_print


class Parser:

    def __init__(self, all_event_types, all_event_attributes):
        """
        Parser class that allows to generate event patterns using instructions.
        :param all_event_types: list of all possible event types to be used in the environment.
        :param all_event_attributes: dictionary of lists of all possible corresponding values for each event type.
        """
        self.all_event_attributes = all_event_attributes
        self.all_event_types = all_event_types
        self.min_max_durations = {"min": 1, "max": 1}

        # TODO (priority 3) establish language for event type and optimise value usage
        # TODO (priority 3) externalise and make value usage independent
        # TODO (priority 3) change for official labelisation function
        self.all_event_types_labels = list_to_labels(all_event_types)
        self.all_event_attributes_labels = {key: list_to_labels(l) for key, l in all_event_attributes.items()}

        # TODO (priority 3) make this prettier later somehow
        self.type_to_label = dict(zip(self.all_event_types, self.all_event_types_labels))
        self.label_to_type = dict(zip(self.all_event_types_labels, self.all_event_types))
        self.attr_to_label = dict()
        self.label_to_attr = dict()
        for attr_name, attr_vals in self.all_event_attributes.items():
            self.attr_to_label[attr_name] = dict(zip(attr_vals, list_to_labels(attr_vals)))
            self.label_to_attr[attr_name] = dict(zip(map(str, list_to_labels(attr_vals)), attr_vals))

    def labelise(self, e_type: str, attributes: dict):
        """
        Associates a label to an event type and a dictionary of attributes.
        In this way we make sure that all associated labels are coherent.

        :param e_type: The event type to be transformed into an integer label.
        :param attributes: The dictionary of attributes to transform. Each value becomes an integer label while parameter names stay unchanged.
        :return: Integer label type and dictionary of integer value attributes.
        """
        e_type = self.type_to_label[e_type]
        attributes = {key: self.attr_to_label[key][value] for key, value in attributes.items()}
        return e_type, attributes

    def noise(self, before):
        t1, t2 = random.uniform(0,before), random.uniform(0,before)
        start, end = min(t1, t2), max(t1, t2)
        noise = self.instantiate()
        noise.set_time(start, end)
        return noise

    # TODO (priority 3) add function to check if values are correct
    def instantiate(self, e_type: str = None, attributes: dict = {}, duration_distribution: dict() = {}):
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
        if e_type not in self.all_event_types:
            e_type = random.choice(self.all_event_types)
        for attr, attr_values in self.all_event_attributes.items():
            if attr not in attributes:
                attributes[attr] = random.choice(attr_values)

        if duration_distribution:
            self.record_duration(duration_distribution["mu"])
        else:
            duration_distribution = self.get_random_duration_dist()

        duration_inst = my_normal(**duration_distribution)
        e_type, attributes = self.labelise(e_type, attributes)
        return Event(e_type, attributes, 0, duration_inst)

    def record_duration(self, duration):
        if duration < self.min_max_durations["min"]:
            self.min_max_durations["min"] = duration
        elif duration > self.min_max_durations["max"]:
            self.min_max_durations["max"] = duration

    def get_random_duration_dist(self):
        sigma = (self.min_max_durations["max"] - self.min_max_durations["min"])/2
        mu = self.min_max_durations["min"] + sigma
        return {"mu": mu, "sigma": sigma}

    def generate_pattern(self, instructions: dict):
        """
        Generated a pattern of events using a dictionary of commands following a particular format.

        :param instructions: The dictionary of commands.
        :return: A list of events that follows the selected instructions.
        """
        event_list = []
        # TODO (priority 3) make same for all parser however problem with same names over configs
        variables = dict()
        for instr_line in instructions:
            if instr_line["command"] == "instantiate":
                event = self.instantiate(*instr_line["parameters"])
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
                # TODO (priority 3) add more errors and tests for correctly used values
                raise ValueError("Unknown allen command: " + str(instr_line["command"]))
        return sorted(event_list)
