import random
from matplotlib import colors
from utils.allen import allen_functions
from Elements.Event import Event


# TODO (priority 4) doc
# TODO (priority 3) rethink class structure and use input all items to generate dictionaries
# TODO (priority 3) rethink labelisation
# TODO (priority 1) add more allen functions
# TODO (priority 1) add noise

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
        self.type_to_label = {all_event_types[i]: i for i in range(len(all_event_types))}
        self.attr_to_label = dict()
        self.label_to_color = dict()
        for attr_name, attr_vals in all_event_attributes.items():
            self.attr_to_label[attr_name] = {attr_vals[i]: i for i in range(len(attr_vals))}
            self.label_to_color[attr_name] = {str(i): attr_vals[i] for i in range(len(attr_vals))}

    def labelise(self, e_type, attributes):
        e_type = self.type_to_label[e_type]
        attributes = {key: self.attr_to_label[key][value] for key, value in attributes.items()}
        return e_type, attributes

    def instantiate(self, e_type: str = None, attributes: dict = {}, duration_dist: (int, int) = (2, 1)):
        if e_type is None:
            e_type = random.choice(self.all_event_types)
        for attr, attr_values in self.all_event_attributes.items():
            if attr not in attributes:
                attributes[attr] = random.choice(attr_values)
        duration_inst = random.normalvariate(*duration_dist)
        duration_inst = max(duration_inst, duration_dist[0] - duration_dist[1])
        e_type, attributes = self.labelise(e_type, attributes)
        return Event(e_type, attributes, 0, duration_inst)

    def generate_pattern(self, instructions):
        event_list = []
        variables = dict()
        for instr in instructions:
            if instr["command"] == "instantiate":
                event = self.instantiate(*instr["parameters"])
                variables[instr["variable_name"]] = event
                if not event_list:
                    event_list.append(event)
            else:
                params = (variables[param] for param in instr["parameters"])
                if instr["command"] == "after":
                    event = allen_functions[instr["command"]](*params, instr["gap_dist"])
                else:
                    event = allen_functions[instr["command"]](*params)
                variables[instr["variable_name"]] = event
                event_list.append(event)
        return sorted(event_list)
