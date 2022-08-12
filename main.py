import random

import plotly.io as pio
import yaml

# instr1 = [{"command": "delay", "parameters": 5},
#           {"command": "instantiate", "parameters": ("A", {"bg": "blue"}, (4, 2)), "variable_name": "a1"},
#           {"command": "instantiate", "parameters": ("C", {"fg": "red"}, (10, 1)), "variable_name": "c1"},
#           {"command": "after", "parameters": ("c1", "a1"), "variable_name": "c1", "other": {"gap_dist": (2, 1)}},
#           {"command": "instantiate", "parameters": ("C", {}, (4, 1)), "variable_name": "c2"},
#           {"command": "during", "parameters": ("c2", "c1"), "variable_name": "c2"},
#           {"command": "instantiate", "parameters": ("A", {}), "variable_name": "a2"},
#           {"command": "met_by", "parameters": ("a2", "c1"), "variable_name": "a2"}]

from mygym.BoxEventEnv import BoxEventEnv
from utils.utils import parse_file, parse_yaml_file

pio.renderers.default = "browser"

"""
TODO after holidays
- Report
- Start tests with exCog
- Write test modules for code and use as excuse to rework code and reformat
    (do this in parallel with setup for excog and documentation)
    - start from tests on simple classes such as box and event
- Implement mini-features for environment
    - Multiple Patterns satisfied by same observation
    - Rethink noise generation and add event specific noise 
    - Noise different from all next events? add different type for noise?
- Cosmetic
    - Rework GUI to separate functions and make more generic 
    - Rework parser to reduce used dictionaries and make more clear
    - Change Event class structure to remove dictionaries and make easir to use
"""


if __name__ == '__main__':

    with open("/home/S3G-LABS/u1226/dev/openchests/config/config.yaml", "r") as f:
        conf = yaml.safe_load(f)

    all_event_types = conf["EVENT_TYPES"]
    all_event_attributes = conf["EVENT_ATTRIBUTES"]

    all_instructions = []
    for file in conf["INSTRUCTIONS"]:
        instr = parse_yaml_file("config/patterns/" + file)
        all_instructions.append(instr)
        print(instr)

    env = BoxEventEnv(instructions=all_instructions,
                      all_event_types=all_event_types,
                      all_event_attributes=all_event_attributes,
                      verbose=False)

    verbose_env = BoxEventEnv(instructions=all_instructions,
                              all_event_types=all_event_types,
                              all_event_attributes=all_event_attributes,
                              verbose=True)

    from stable_baselines3 import A2C
    from stable_baselines3.common.env_util import make_vec_env

    # Instantiate the env
    # wrap it
    env = make_vec_env(lambda: env, n_envs=1)
    verbose_env = make_vec_env(lambda: verbose_env, n_envs=1)

    # Train the agent
    print("Learning")
    model = A2C('MultiInputPolicy', env, verbose=1).learn(10000)
    # model = A2C('MultiInputPolicy', env, verbose=1)

    # Test the trained agent
    obs = verbose_env.reset()
    verbose_env.render()
    n_steps = 100
    print("------------------------ START -------------------------")
    for step in range(n_steps):
        action, _ = model.predict(obs, deterministic=True)
        sure_action = [[1, 1]]
        empty_action = [[0, 0]]
        random_action = [[random.randint(0, 1) for i in range(2)]]
        print("Step {}".format(step + 1))
        print("Action: ", action)
        obs, reward, done, info = verbose_env.step(action)
        verbose_env.render()
        print('obs =', obs, 'reward=', reward, 'done=', done)
        if done:
            # Note that the VecEnv resets automatically
            # when a done signal is encountered
            print("Goal reached!", "reward=", reward)
            break
