import numpy as np
import gymnasium as gym
import yaml
from gymnasium.spaces import Dict, MultiBinary, Discrete, Box

from openthechests.openthechests.src.OpenTheChests import OpenTheChests
from openthechests.openthechests.src.utils.helper_functions import boxes_to_discrete, parse_yaml_file


class OpenTheChestsGym(gym.Env):
    """
    A Gym-compatible wrapper for the symbolic box-opening environment `OpenTheChests`.

    This class integrates the custom environment into the OpenAI Gym interface,
    allowing it to be used with reinforcement learning libraries like Stable Baselines3.

    It supports both:
    - Discrete actions (single integer for pressing box buttons)
    - Multi-binary actions (list of 0s and 1s for each box)

    It also formats observations for SB3 compatibility if requested.

    Parameters
    ----------
    instructions : list
        List of instruction sets defining each pattern (one per box).
    all_event_types : list[str]
        List of all valid symbolic event types.
    all_event_attributes : dict[str, list]
        Dictionary mapping attribute names to possible values for normal events.
    all_noise_types : list[str]
        List of symbolic types that may appear as noise.
    all_noise_attributes : dict[str, list]
        Dictionary mapping attribute names to possible values for noise events.
    discrete : bool, optional
        If True, use single-integer actions instead of binary lists (default: False).
    verbose : bool, optional
        If True, print detailed logs during environment execution (default: False).
    stb3 : bool, optional
        If True, format observations to be compatible with Stable Baselines3 (default: True).
    """

    ...

    def __init__(self, instructions: list,
                 all_event_types,
                 all_event_attributes,
                 all_noise_types,
                 all_noise_attributes,
                 discrete=False,
                 verbose=False,
                 stb3=True):
        """
        Initializes the Gym-compatible wrapper around the OpenTheChests environment.

        This constructor builds an internal `OpenTheChests` environment and sets up
        the required Gym spaces (`action_space`, `observation_space`) based on configuration.

        Parameters
        ----------
        instructions : list
            A list of pattern instructions, one for each interactive box.
            Each pattern is a list of commands like "instantiate", "after", etc.
        all_event_types : list[str]
            All symbolic event types allowed in the environment (e.g., ["A", "B", "C"]).
        all_event_attributes : dict[str, list]
            Dictionary mapping attribute names to valid values for **normal events**.
            Example: {"bg": ["red", "blue"], "fg": ["white", "black"]}
        all_noise_types : list[str]
            Event types that can only appear as **noise**, not as pattern-relevant events.
        all_noise_attributes : dict[str, list]
            Same as `all_event_attributes`, but used only for noise event generation.
        discrete : bool, optional
            If True, use a single integer action space (i.e., `Discrete(2^n)`).
            If False, use a binary vector of length `n` (`MultiBinary(n)`) (default: False).
        verbose : bool, optional
            If True, enables debug printouts in the underlying environment (default: False).
        stb3 : bool, optional
            If True, formats all observations to comply with Stable Baselines3 requirements
            (flattened, no nested dicts). Default is True.

        Notes
        -----
        - The `action_space` will either be:
            - `Discrete(2^n)` if `discrete=True`
            - `MultiBinary(n)` if `discrete=False`
        - The `observation_space` will always be a flat `gym.spaces.Dict` with keys:
            - "active", "open" (MultiBinary)
            - "e_type" (Discrete)
            - One key per attribute (Discrete)
            - "start", "end", "duration" (Box)
        """

        super(OpenTheChestsGym, self).__init__()

        # Initialize the wrapped custom environment
        self.env = OpenTheChests(
            instructions=instructions,
            all_event_types=all_event_types,
            all_event_attributes=all_event_attributes,
            all_noise_types=all_noise_types,
            all_noise_attributes=all_noise_attributes,
            verbose=verbose,
            discrete=discrete,
            stb3=stb3
        )

        num_boxes = self.env.get_num_boxes()
        num_event_types = len(self.env.parser.all_types)

        # Define action space: either single discrete integer or multi-binary button presses
        if discrete:
            self.action_space = Discrete(boxes_to_discrete(num_boxes))
        else:
            self.action_space = MultiBinary(num_boxes)

        # Define observation space
        attr_space = {
            attr_name: Discrete(len(attr_values))
            for attr_name, attr_values in self.env.parser.all_attributes.items()
        }

        self.observation_space = Dict({
            "active": MultiBinary(num_boxes),
            "open": MultiBinary(num_boxes),
            "e_type": Discrete(num_event_types),
            **attr_space,
            "start": Box(low=0.0, high=np.inf, shape=(1,), dtype=np.float32),
            "end": Box(low=0.0, high=np.inf, shape=(1,), dtype=np.float32),
            "duration": Box(low=0.0, high=np.inf, shape=(1,), dtype=np.float32)
        })

    @classmethod
    def from_config_file(cls,
                         env_config_file: str,
                         pattern_configs_folder: str = None,
                         verbose=False,
                         stb3=True,
                         discrete=False):
        """
        Instantiates an OpenTheChestsGym environment from a YAML config file.

        This method:
        - Parses the event and noise type/attribute definitions.
        - Loads each pattern from separate YAML files.
        - Builds and returns the fully configured environment.

        Parameters
        ----------
        env_config_file : str
            Path to the main environment config YAML file.
        pattern_configs_folder : str, optional
            Directory containing pattern YAML files. If None, uses the same directory as `env_config_file`.
        verbose : bool, optional
            Enable debug print statements (default: False).
        stb3 : bool, optional
            Whether to format observations for Stable Baselines3 (default: True).
        discrete : bool, optional
            Whether to use discrete action space (default: False).

        Returns
        -------
        OpenTheChestsGym
            A fully initialized Gym environment instance.
        """
        with open(env_config_file, "r") as f:
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
        if pattern_configs_folder is None:
            pattern_configs_folder = "/".join(env_config_file.split("/")[:-1])
        for pattern_conf_file in conf["INSTRUCTIONS"]:
            instr = parse_yaml_file(pattern_configs_folder + "/" + pattern_conf_file)
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
        """
        Executes one environment step with the given action.

        Parameters
        ----------
        action : int or list[int]
            Either an integer (if `discrete=True`) or a list of 0s and 1s
            indicating which box buttons to press.

        Returns
        -------
        observation : dict
            Dictionary containing box states and current context event.
        reward : int
            Cumulative reward from this action.
        done : bool
            Whether the episode has ended.
        truncated : None
            Placeholder for Gym's API compatibility (unused here).
        info : dict
            Metadata (currently unused).
        """
        obs, reward, done, info = self.env.step(action)
        return obs, reward, done, None, info

    def reset(self):
        """
        Resets the environment to a new episode and returns the initial observation.

        Returns
        -------
        observation : dict
            The initial observation of the environment.
        """
        return self.env.reset()

    def render(self):
        self.env.render()

    def get_attributes(self):
        """
        Returns a dictionary of all attributes used in event definitions.

        Returns
        -------
        dict[str, list]
            Mapping of attribute names to their possible values.
        """
        return self.env.parser.all_attributes

    def get_types(self):
        """
        Returns a list of all symbolic event and noise types.

        Returns
        -------
        list[str]
            List of type names.
        """
        return self.env.parser.all_types

    def get_otc(self):
        """
        Returns the internal OpenTheChests environment instance.

        Useful for accessing detailed behavior or visuals not exposed through Gym.

        Returns
        -------
        OpenTheChests
            The wrapped base environment.
        """
        return self.env
