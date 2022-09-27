from src.env.Parser import Parser
from examples.create_env import all_event_attributes, all_noise_attributes, all_event_types, all_noise_types
from examples.instructions import instructions

p = Parser(all_event_types, all_noise_types, all_event_attributes, all_noise_attributes)

example_labelised = p.labelise("A", {"fg": "blue"})
example_labelised = p.labelise("A", {"fg": "blue", "bg": "red"})

# ignore delay and noise commands
event_list = p.generate_pattern(instructions[0][2:])

bad_instructions = [{'command': 'instantiate', 'parameters': ('xxx', {'bg': 'blue', 'fg': 'blue'}, {'mu': 5, 'sigma': 2}),
                     'variable_name': 'distinct'},
                    {'command': 'instantiate',
                     'parameters': ('E', {'bg': 'pink', 'fg': 'green'}, {'mu': 6, 'sigma': 2}), 'variable_name': 'e1'},
                    {'command': 'instantiate', 'parameters': ('E', {'bg': 'red', 'fg': 'green'}, {'mu': 8, 'sigma': 0}),
                     'variable_name': 'e2'},
                    {'command': 'instantiate',
                     'parameters': ('C', {'bg': 'orange', 'fg': 'red'}, {'mu': 5, 'sigma': 1}), 'variable_name': 'c1'},
                    {'command': 'met_by', 'parameters': ['e2', 'c1'], 'variable_name': 'e2', 'other': {}},
                    {'command': 'during', 'parameters': ['e1', 'e2'], 'variable_name': 'e1', 'other': {}},
                    {'command': 'after', 'parameters': ['distinct', 'e2'], 'variable_name': 'distinct',
                     'other': {'gap_dist': {'mu': 4, 'sigma': 1}}}]


p.generate_pattern(bad_instructions)
