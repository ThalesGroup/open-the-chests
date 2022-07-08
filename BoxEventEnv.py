import numpy as np
import gym
from gym import spaces

from Dynamics.Environment import Environment


class BoxEventEnv(gym.Env):

    def __init__(self, instructions: list, all_event_types, all_event_attributes, verbose):
        super(BoxEventEnv, self).__init__()
        self.verbose = verbose
        self.all_event_attributes = all_event_attributes
        self.all_event_types = all_event_types
        self.instructions = instructions

        self.env = Environment(instructions, all_event_types, all_event_attributes, verbose)
        self.action_space = spaces.MultiBinary(self.env.num_boxes)

        # TODO add state of boxes to observations
        self.observation_space = spaces.MultiBinary([2, self.env.num_boxes])

    def step(self, action):
        pass

    def reset(self):
        pass

    def render(self, mode="human"):
        pass
