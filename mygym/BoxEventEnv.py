import numpy as np
import gym
import yaml
from gym.spaces import Dict, MultiBinary, Discrete, Box

from Dynamics.Environment import Environment
from globals import ENV_PATTERNS_FOLDER
from utils.utils import parse_yaml_file, bug_print


class BoxEventEnv(gym.Env):

    def __init__(self, instructions: list,
                 all_event_types,
                 all_event_attributes,
                 all_noise_types,
                 all_noise_attributes,
                 discrete=False,
                 verbose=False):
        super(BoxEventEnv, self).__init__()
        self.verbose = verbose
        self.all_event_attributes = all_event_attributes
        self.all_event_types = all_event_types
        self.instructions = instructions

        self.env = Environment(instructions=instructions,
                               all_event_types=all_event_types,
                               all_event_attributes=all_event_attributes,
                               all_noise_types=all_noise_types,
                               all_noise_attributes=all_noise_attributes,
                               verbose=verbose,
                               discrete=discrete,
                               stb3=True)

        if discrete:
            self.action_space = Discrete(2**self.env.num_boxes - 1)
        else:
            self.action_space = MultiBinary(self.env.num_boxes)

        num_types = len(self.env.parser.all_types)
        attr_space = {attr_name: Discrete(len(attr_values)) for (attr_name, attr_values) in
                      self.env.parser.all_attributes.items()}

        self.observation_space = Dict({
            "active": MultiBinary(self.env.num_boxes),
            "open": MultiBinary(self.env.num_boxes),
            "e_type": Discrete(num_types),
            **attr_space,
            "start": Box(low=0, high=np.inf, shape=(1,)),
            "end": Box(low=0, high=np.inf, shape=(1,)),
            "duration": Box(low=0, high=np.inf, shape=(1,))
        })

    @classmethod
    def from_config_file(cls, config_file_name, verbose=False, discrete=False):
        with open(config_file_name, "r") as f:
            conf = yaml.safe_load(f)

        all_event_types = conf["EVENT_TYPES"]["NORMAL"]
        all_event_attributes = conf["EVENT_ATTRIBUTES"]["NORMAL"]

        all_noise_types = []
        if "NOISE" in conf["EVENT_TYPES"]:
            all_noise_types = conf["EVENT_TYPES"]["NOISE"]
        all_noise_attributes = []
        if "NOISE" in conf["EVENT_ATTRIBUTES"]:
            all_noise_attributes = conf["EVENT_ATTRIBUTES"]["NOISE"]

        all_instructions = []
        for file in conf["INSTRUCTIONS"]:
            instr = parse_yaml_file(ENV_PATTERNS_FOLDER + file)
            # print(file)
            # bug_print(instr)
            all_instructions.append(instr)

        env = cls(instructions=all_instructions,
                  all_event_types=all_event_types,
                  all_event_attributes=all_event_attributes,
                  all_noise_types=all_noise_types,
                  all_noise_attributes=all_noise_attributes,
                  verbose=verbose,
                  discrete=discrete)

        return env

    def step(self, action):
        obs, reward, done, info = self.env.step(action)
        return obs, reward, done, info

    def reset(self):
        return self.env.reset()

    # TODO (priority 3) add different rendering modes of possible
    def render(self, mode="human"):
        self.env.render()
