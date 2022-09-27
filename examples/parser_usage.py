from examples.create_env.create_base_env import all_event_types, all_noise_types, all_event_attributes, \
    all_noise_attributes
from src.env.Parser import Parser
from examples.create_env.instructions import instructions

# instantiate a parser using all event information
p = Parser(all_event_types, all_noise_types, all_event_attributes, all_noise_attributes)

# labelise event information
example_labelised = p.labelise("A", {"fg": "blue"})
example_labelised = p.labelise("A", {"fg": "blue", "bg": "red"})

# ignore delay and noise commands (1st and 2nd in instructions list)
# generate an event list from the instructions
event_list = p.generate_pattern(instructions[0][2:])


