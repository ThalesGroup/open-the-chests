import numpy as np
import gym
import yaml
from gym.spaces import Dict, MultiBinary, Discrete, Box

from src.openthechests.env.Environment import Environment
from src.openthechests.src import parse_yaml_file, boxes_to_discrete


class BoxEventEnv(gym.Env):

    def __init__(self, instructions: list,
                 all_event_types,
                 all_event_attributes,
                 all_noise_types,
                 all_noise_attributes,
                 discrete=False,
                 verbose=False,
                 stb3=True):
        """
        Defines a gym compatible wrapper for the box event environment.
        Allows defining observation and action spaces used for model setup.

        :param instructions: List of commands allowing to define patterns for each box
        :param all_event_types: List of all possible event types that can take place
        :param all_event_attributes: Dictionary of al event types with a corresponding list of possible values
        :param all_noise_types: List of all possible types to be used for noise generation only
        :param all_noise_attributes: List of all possible types to be used for noise generation only
        :param discrete: Accept actions under integer format instead of binary vector
        :param verbose: Print details when executing for debugging
        :param stb3: Use environment with stable baselines 3
        """
        super(BoxEventEnv, self).__init__()

        # TODO (priority 3) switch to inherit and initialise from both gym and base env
        # instantiate environment
        self.env = Environment(instructions=instructions,
                               all_event_types=all_event_types,
                               all_event_attributes=all_event_attributes,
                               all_noise_types=all_noise_types,
                               all_noise_attributes=all_noise_attributes,
                               verbose=verbose,
                               discrete=discrete,
                               stb3=stb3)

        # define action space depending on usage of discrete actions or not
        if discrete:
            self.action_space = Discrete(boxes_to_discrete(self.env.num_boxes))
        else:
            self.action_space = MultiBinary(self.env.num_boxes)

        # Define a space for observations using environment information
        num_event_types = len(self.env.parser.all_types)
        attr_space = {attr_name: Discrete(len(attr_values)) for (attr_name, attr_values) in
                      self.env.parser.all_attributes.items()}

        self.observation_space = Dict({
            "active": MultiBinary(self.env.num_boxes),
            "open": MultiBinary(self.env.num_boxes),
            "e_type": Discrete(num_event_types),
            **attr_space,
            "start": Box(low=0, high=np.inf, shape=(1,)),
            "end": Box(low=0, high=np.inf, shape=(1,)),
            "duration": Box(low=0, high=np.inf, shape=(1,))
        })

    @classmethod
    def from_config_file(cls, config_file_name, verbose=False, stb3=True, discrete=False):
        """
        Use a YAML configuration file to define an environment.

        :param stb3: Output format observation adapted to stable baselines or not.
        :param config_file_name: The configuration file.
        :param verbose: Give information during environment execution.
        :param discrete: Use discrete actions.
        :return: The newly defined environment.
        """
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
        # TODO (priority 2) fix this to either take folder in param or something else
        config_file_instr_path = "/".join(config_file_name.split("/")[:-1])
        for file in conf["INSTRUCTIONS"]:
            instr = parse_yaml_file(config_file_instr_path + "/" + file)
            all_instructions.append(instr)

        env = cls(instructions=all_instructions,
                  all_event_types=all_event_types,
                  all_event_attributes=all_event_attributes,
                  all_noise_types=all_noise_types,
                  all_noise_attributes=all_noise_attributes,
                  verbose=verbose,
                  stb3=stb3,
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
