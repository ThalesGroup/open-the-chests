import random

from Dynamics.utils import allen_functions
from Elements.Event import Event


class Parser:

    def __init__(self, all_event_types, all_event_attributes):
        self.all_event_attributes = all_event_attributes
        self.all_event_types = all_event_types

    def instantiate(self, e_type: str = None, attributes: dict = {}, duration_dist: (int, int) = (2, 1)):
        if e_type is None:
            e_type = random.choice(self.all_event_types)
        for attr, attr_values in self.all_event_attributes.items():
            if attr not in attributes:
                attributes[attr] = random.choice(attr_values)
        duration_inst = random.normalvariate(*duration_dist)
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
        return event_list
