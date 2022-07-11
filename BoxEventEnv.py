import numpy as np
import gym
from gym.spaces import Dict, MultiBinary, Discrete, Box

from Dynamics.Environment import Environment
from utils.EventSpace import EventSpace


class BoxEventEnv(gym.Env):

    def __init__(self, instructions: list, all_event_types, all_event_attributes, verbose):
        super(BoxEventEnv, self).__init__()
        self.verbose = verbose
        self.all_event_attributes = all_event_attributes
        self.all_event_types = all_event_types
        self.instructions = instructions

        self.env = Environment(instructions=instructions,
                               all_event_types=all_event_types,
                               all_event_attributes=all_event_attributes,
                               verbose=verbose,
                               stb3=True)

        self.action_space = MultiBinary(self.env.num_boxes)

        num_types = len(all_event_types)
        attr_space = {attr_name: Discrete(len(attr_values)) for (attr_name, attr_values) in
                      all_event_attributes.items()}

        self.observation_space = Dict({
            "active": MultiBinary(self.env.num_boxes),
            "open": MultiBinary(self.env.num_boxes),
            "e_type": Discrete(num_types),
            **attr_space,
            "start": Box(low=0, high=np.inf, shape=(1,)),
            "end": Box(low=0, high=np.inf, shape=(1,)),
            "duration": Box(low=0, high=np.inf, shape=(1,))
        })

    def step(self, action):
        return self.env.step(action)

    def reset(self):
        return self.env.reset()

    def render(self, mode="human"):
        pass
