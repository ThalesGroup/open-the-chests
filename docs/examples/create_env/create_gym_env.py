from docs.examples.create_env.env_info import all_event_types, all_event_attributes, all_noise_types, \
    all_noise_attributes
from docs.examples.create_env.instructions import instructions
from openthechests.src.OpenTheChestsGym import OpenTheChestsGym

"""
Example : Create environment with gym wrapper
"""

# define a list of all possible event types to be used by the instructions
# initialise environment using class and instructions list

env = OpenTheChestsGym(instructions=instructions,
                       all_event_types=all_event_types,
                       all_event_attributes=all_event_attributes,
                       all_noise_types=all_noise_types,
                       all_noise_attributes=all_noise_attributes,
                       verbose=False,
                       discrete=True,
                       stb3=True)

# initialise class using a YAML configuration file
from_config = OpenTheChestsGym.from_config_file(env_config_file="example_config/multiple_per_box.yaml",
                                                verbose=False,
                                                stb3=True)

# both environments are the same
assert from_config.env.parser.all_types == env.env.parser.all_types
for i in range(len(from_config.env.patterns[0].instruction)):
    assert from_config.env.patterns[0].instruction[i] == env.env.patterns[0].instruction[i]

# use gym action sampling to take random actions and observe environment for 10 steps
obs = env.reset()
# env.render()
# don't forget to reset the environment before using it
for step in range(100):
    # Take a random action
    action = env.action_space.sample()
    print("Action: ", action)
    obs, reward, done, info = env.step(action)
    print('obs =', obs, 'reward=', reward, 'done=', done)
    # env.render()
