import random
from examples.create_env.env_info import all_event_types, all_event_attributes, all_noise_types, \
    all_noise_attributes
from examples.create_env.instructions import instructions
from src.openthechests.env.OpenTheChests import OpenTheChests

"""
Example : Create environment without gym wrapper
"""


# initialise environment
env = OpenTheChests(instructions=instructions,
                    all_event_types=all_event_types,
                    all_event_attributes=all_event_attributes,
                    all_noise_types=all_noise_types,
                    all_noise_attributes=all_noise_attributes,
                    verbose=True,
                    stb3=False)

# reset environment before usage to get first observation and generate all data
first_obs = env.reset()

# define a binary vector with the same length as the number of boxes
# this will define the action of which buttons to press
example_action = [[random.randint(0, 1) for i in range(env._num_boxes)]]

# apply the action and evolve the environment to get the next observation
obs, reward, done, info = env.step(example_action)

# it is possible to get the last observation when needed
same_obs = env.get_observations()

# it is also possible to check if the game has ended
end = env.check_end()
