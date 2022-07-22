import random

from utils.allen import allen_functions
from Elements.Event import Event

# TODO (priority 4) doc
# TODO (priority 3) rethink class structure and use input all items to generate dictionaries
# TODO (priority 3) rethink labelisation
# TODO (priority 1) add more allen functions
# TODO (priority 1) add noise
from utils.utils import list_to_labels, bug_print


class Parser:

    def __init__(self, all_event_types, all_event_attributes):
        """
        Parser class that allows to generate event patterns using instructions
        :param all_event_types: list of all possible event types to be used in the environment
        :param all_event_attributes: dictionary of lists of all possible corresponding values for each event type
        """
        self.all_event_attributes = all_event_attributes
        self.all_event_types = all_event_types

        # TODO (priority 3) establish language for event type and optimise value usage
        # TODO (priority 3) externalise and make value usage independent
        # TODO (priority 3) change for official labelisation function
        self.all_event_types_labels = list_to_labels(all_event_types)
        self.all_event_attributes_labels = {key: list_to_labels(l) for key, l in all_event_attributes.items()}

        self.type_to_label = dict(zip(self.all_event_types, self.all_event_types_labels))
        self.label_to_type = dict(zip(self.all_event_types_labels, self.all_event_types))
        self.attr_to_label = dict()
        self.label_to_attr = dict()
        # TODO (priority 3) make this prettier later somehow
        for attr_name, attr_vals in all_event_attributes.items():
            self.attr_to_label[attr_name] = dict(zip(attr_vals, list_to_labels(attr_vals)))
            self.label_to_attr[attr_name] = dict(zip(map(str,list_to_labels(attr_vals)), attr_vals))

    def labelise(self, e_type, attributes):
        e_type = self.type_to_label[e_type]
        attributes = {key: self.attr_to_label[key][value] for key, value in attributes.items()}
        return e_type, attributes

    # TODO (priority 3) add function to check if values are correct
    def instantiate(self, e_type: str = None, attributes: dict = {}, duration_distribution: (int, int) = (2, 1)):
        if e_type not in self.all_event_types:
            e_type = random.choice(self.all_event_types)
        for attr, attr_values in self.all_event_attributes.items():
            if attr not in attributes:
                attributes[attr] = random.choice(attr_values)
        duration_inst = random.normalvariate(*duration_distribution)
        duration_inst = max(duration_inst, duration_distribution[0] - duration_distribution[1])
        e_type, attributes = self.labelise(e_type, attributes)
        return Event(e_type, attributes, 0, duration_inst)

    def generate_pattern(self, instructions):
        event_list = []
        variables = dict()
        for instr_line in instructions:
            if instr_line["command"] == "instantiate":
                event = self.instantiate(*instr_line["parameters"])
                variables[instr_line["variable_name"]] = event
                if not event_list:
                    event_list.append(event)
            else:
                # allen command for positioning
                events = (variables[var_name] for var_name in instr_line["parameters"])
                allen_op = instr_line["command"]
                bonus_params = instr_line["other"] if "other" in instr_line else dict()
                event = allen_functions[allen_op](*events, **bonus_params)
                variables[allen_op] = event
                event_list.append(event)
        return sorted(event_list)
