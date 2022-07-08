import numpy as np
import gym
from gym.spaces import Dict, MultiBinary

from Dynamics.Environment import Environment
from utils.EventSpace import EventSpace


class BoxEventEnv(gym.Env):

    def __init__(self, instructions: list, all_event_types, all_event_attributes, verbose):
        super(BoxEventEnv, self).__init__()
        self.verbose = verbose
        self.all_event_attributes = all_event_attributes
        self.all_event_types = all_event_types
        self.instructions = instructions

        self.env = Environment(instructions, all_event_types, all_event_attributes, verbose)
        self.action_space = MultiBinary(self.env.num_boxes)

        # TODO add state of boxes to observations
        state_space_dict = Dict({
            "active": MultiBinary(self.env.num_boxes),
            "open": MultiBinary(self.env.num_boxes)
        })
        self.observation_space = Dict({
            "state": state_space_dict,
            "context": EventSpace(all_event_types, all_event_attributes)
        })

    def step(self, action):
        return self.env.step(action)

    def reset(self):
        return self.env.reset()

    def render(self, mode="human"):
        pass
