from re import Pattern
from examples.create_env.instructions import instructions
from examples.create_env.env_info import all_event_types, all_noise_types, all_event_attributes, \
    all_noise_attributes
from src.openthechests.env.elements.Parser import Parser
from src.openthechests.env.elements.Event import Event
from src.openthechests.env.elements.InteractiveBox import InteractiveBox


# create an event with the given attributes and start end _time
e = Event("A", {"attr1": "blue", "attr2": "green"}, 5, 10)
shifted_forward = e.shifted(10)
shifted_backward = e.shifted(-5)


# instantiate a parser using all event information
parser = Parser(all_event_types, all_noise_types, all_event_attributes, all_noise_attributes)

# add noise to the instruction
instruction = instructions[0]
# use line where command == noise
instruction[1]["parameters"] = 0.5

# define a pattern with the help of a list of instructions
pattern = Pattern(parser=parser,
                  instruction=instruction,
                  verbose=False)

# generate a list of noise event proportional to a list length
noise_list = pattern.generate_noise_events(pattern_end=20, pattern_len=10)

# generate events following the instructions, generate noise and fill the pattern stack with events
# starting at _time t
pattern.fill_event_stack(t=15)

# get the next event on the stack
next_on_stack = pattern.get_next()

# define a box using the selected pattern
box = InteractiveBox(id=42,
                     pattern=pattern,
                     verbose=False)
