import numpy as np
from gym.spaces import Dict, Discrete, Box


"""
OUTDATED (However keeping it for future needs.)
Defines and allows to sample custom space type for events.
Due to stable baselines accepting only dictionary formats, this is not currently used. 
"""

class EventSpace(Dict):

    def __init__(self, all_event_types, all_event_attributes):
        num_types = len(all_event_types)
        attr_space = {attr_name: Discrete(len(attr_values)) for (attr_name, attr_values) in
                      all_event_attributes.items()}

        super(EventSpace, self) \
            .__init__({
                "type": Discrete(num_types),
                "attributes": Dict(attr_space),
                "t_start": Box(low=0, high=np.inf, shape=(1,)),
                "t_end": Box(low=0, high=np.inf, shape=(1,))
            })

    def sample(self):
        event = super(EventSpace, self).sample()
        event["t_end"] = event["t_start"] + event["t_end"]
        return event
