import random
from src.env.Environment import Environment
from examples.create_env.instructions import instructions

"""
Example : Create environment without gym wrapper
"""


# define a list of all possible event types to be used by the instructions

all_event_types = ['A', 'B', 'C', 'D', 'E']

# define a distraction that gives ll possible values for each attribute
all_event_attributes = {'fg': ['red', 'blue', 'green', 'orange', 'pink'],
                        'bg': ['red', 'blue', 'green', 'orange', 'pink']}

# do the same for noise events
# it is recommended to give values different from the ones used for event generation
all_noise_types = ['G', 'H', 'F']
all_noise_attributes = {'fg': ['yellow', 'purple', 'black'], 'bg': ['yellow', 'purple', 'black']}

# initialise environment
env = Environment(instructions=instructions,
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
example_action = [[random.randint(0, 1) for i in range(env.num_boxes)]]

# apply the action and evolve the environment to get the next observation
obs, reward, done, info = env.step(example_action)

# it is possible to get the last observation when needed
same_obs = env.get_observations()

# it is also possible to check if the game has ended
end = env.check_end()
