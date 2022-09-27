"""
Example : Create environment with gym wrapper
"""

# define a list of all possible event types to be used by the instructions
from examples.create_env.instructions import instructions
from src.BoxEventEnv import BoxEventEnv

all_event_types = ['A', 'B', 'C', 'D', 'E']

# define a distraction that gives ll possible values for each attribute
all_event_attributes = {'fg': ['red', 'blue', 'green', 'orange', 'pink'],
                        'bg': ['red', 'blue', 'green', 'orange', 'pink']}

# do the same for noise events
# it is recommended to give values different from the ones used for event generation
all_noise_types = ['G', 'H', 'F']
all_noise_attributes = {'fg': ['yellow', 'purple', 'black'], 'bg': ['yellow', 'purple', 'black']}

# initialise environment using class and instructions list
env = BoxEventEnv(instructions=instructions,
                  all_event_types=all_event_types,
                  all_event_attributes=all_event_attributes,
                  all_noise_types=all_noise_types,
                  all_noise_attributes=all_noise_attributes,
                  verbose=False,
                  discrete=False,
                  stb3=True)

# initialise class using a YAML configuration file
from_config = BoxEventEnv.from_config_file(config_file_name="examples/create_env/example_config/multiple_per_box.yaml",
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
for step in range(10):
    # Take a random action
    action = env.action_space.sample()
    print("Action: ", action)
    obs, reward, done, info = env.step(action)
    print('obs =', obs, 'reward=', reward, 'done=', done)
    # env.render()
