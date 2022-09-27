from examples.create_env.env_info import all_event_types, all_event_attributes, all_noise_types, all_noise_attributes
from src.env.GUI import BoxEventGUI
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

# make a noise event that ends before the time t
noise_event = p.make_noise(before=10)

# make an event
completely_random_event = p.make_event()
only_typed_event = p.make_event(e_type="A")
event = p.make_event(e_type="A", attributes={"fg": "blue", "bg": "red"},
                     duration_distribution=dict(mu=20, sigma=10))

# here we give an example of how to print an event list using the GUI
# show image in browser
import plotly.io as pio
pio.renderers.default = "browser"

GUI = BoxEventGUI(num_patterns=1, attr_to_color=p.all_attributes)
GUI.print_event_list(event_list=event_list,
                     show=True,
                     current_time=1,
                     bg_color="mediumpurple")
