from copy import deepcopy

from docs.examples.create_env.instructions import instructions
from docs.examples.create_env.env_info import all_event_types, all_noise_types, all_event_attributes, all_noise_attributes
from openthechests.src.elements.Generator import Generator
from openthechests.src.elements.Parser import Parser
from openthechests.src.elements.Event import Event
from openthechests.src.elements.Pattern import Pattern

# Create an event with the given attributes and start end time
e = Event("A", {"attr1": "blue", "attr2": "green"}, 5, 10)
shifted_forward = e.shifted(10)
shifted_backward = e.shifted(-5)

# Instantiate a parser using all event information
parser = Parser(all_event_types, all_noise_types, all_event_attributes, all_noise_attributes)

# Add noise to the instruction
instruction = instructions[0]
instruction[1]["parameters"] = 0.5

# Define a pattern with the help of a list of instructions
pattern_id = 1
pattern = Pattern(instruction=instruction, id=pattern_id)

# Instantiate a generator
generator = Generator(parser=parser, patterns=[pattern])

# Reset the generator to initialize the event stacks
generator.reset()

expected_events = deepcopy(generator.event_stacks)
print(f"Expected events to be generated: {expected_events}")

# Get the 5 next events from the generator
for i in range(5):
    next_event, signal = generator.next_event()
    expected_event = expected_events[pattern_id][i]
    print(f"Next event: {next_event}, Signal: {signal}")
    assert expected_event == next_event

    # Get the current timeline of events
    next_events = generator.get_timeline()
    print(f"Current timeline: {next_events}")

# Disable the timeline for a specific pattern (if needed)
generator.disable_timeline(pattern_id=1)

# Get the current (empty) timeline of events
timeline = generator.get_timeline()
print(f"Empty timeline after disable: {timeline}")


