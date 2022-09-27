# define a list of all possible event types to be used by the instructions
all_event_types = ['A', 'B', 'C', 'D', 'E']

# define a dictionary that gives ll possible values for each attribute
all_event_attributes = {'fg': ['red', 'blue', 'green', 'orange', 'pink'],
                        'bg': ['red', 'blue', 'green', 'orange', 'pink']}

# do the same for noise events
# it is recommended to give values different from the ones used for event generation
all_noise_types = ['G', 'H', 'F']
all_noise_attributes = {'fg': ['yellow', 'purple', 'black'], 'bg': ['yellow', 'purple', 'black']}