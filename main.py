# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import random

from BoxEventEnv import BoxEventEnv
from Dynamics.Environment import Environment

# TODO (priority 1) add config

import plotly.io as pio

pio.renderers.default = "browser"


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # define patterns to be used for boxes

    all_event_types = ["A", "B", "C"]
    all_event_attributes = {"fg": ["red", "blue", "green"], "bg": ["red", "blue", "green"]}

    # all_event_types, all_event_attributes = numerise_types_and_attributes(all_event_types, all_event_attributes)

    print(all_event_types)
    print(all_event_attributes)

    instr1 = [{"command": "delay", "parameters": 5},
              {"command": "instantiate", "parameters": ("A", {"bg": "blue"}, (4, 2)), "variable_name": "a1"},
              {"command": "instantiate", "parameters": ("C", {"fg": "red"}, (10, 1)), "variable_name": "c1"},
              {"command": "after", "parameters": ("c1", "a1"), "variable_name": "c1", "gap_dist": (2, 1)},
              {"command": "instantiate", "parameters": ("C", {}, (4, 1)), "variable_name": "c2"},
              {"command": "during", "parameters": ("c2", "c1"), "variable_name": "c2"},
              {"command": "instantiate", "parameters": ("A",), "variable_name": "a2"},
              {"command": "met_by", "parameters": ("a2", "c1"), "variable_name": "c1"}]

    instr2 = [{"command": "delay", "parameters": 7},
              {"command": "instantiate", "parameters": ("B", {"bg": "blue"}, (4, 2)), "variable_name": "b1"},
              {"command": "instantiate", "parameters": ("B", {"fg": "red"}, (10, 1)), "variable_name": "b2"},
              {"command": "after", "parameters": ("b2", "b1"), "variable_name": "b2", "gap_dist": (2, 1)}]

    instr3 = [{"command": "delay", "parameters": 7},
              {"command": "instantiate", "parameters": ("B", {"bg": "blue"}, (4, 2)), "variable_name": "b1"},
              {"command": "instantiate", "parameters": ("B", {"fg": "red"}, (10, 1)), "variable_name": "b2"},
              {"command": "after", "parameters": ("b2", "b1"), "variable_name": "b2", "gap_dist": (2, 1)}]

    all_instructions = [instr1, instr2]

    # env = Environment(instructions=all_instructions,
    #                   all_event_types=all_event_types,
    #                   all_event_attributes=all_event_attributes,
    #                   verbose=False)

    env = BoxEventEnv(instructions=all_instructions,
                      all_event_types=all_event_types,
                      all_event_attributes=all_event_attributes,
                      verbose=False)

    verbose_env = BoxEventEnv(instructions=all_instructions,
                              all_event_types=all_event_types,
                              all_event_attributes=all_event_attributes,
                              verbose=True)

    from stable_baselines3.common.env_checker import check_env

    # env.fill_event_stack()
    # done = False
    # while not done:
    # # for i in range(10):
    #     action = [random.randint(0, 1) for i in range(2)]
    #     # action = [1,1]
    #     reward, observation, done, info = env.step(action)
    #     print(observation)
    #
    # check_env(env, warn=True)

    # env.reset()

    from stable_baselines3 import A2C
    from stable_baselines3.common.env_util import make_vec_env

    # Instantiate the env
    # wrap it
    env = make_vec_env(lambda: env, n_envs=1)
    verbose_env = make_vec_env(lambda: verbose_env, n_envs=1)

    # Train the agent
    print("Learning")
    model = A2C('MultiInputPolicy', env, verbose=1)  # .learn(5000)

    # Test the trained agent
    obs = verbose_env.reset()
    n_steps = 100
    print("------------------------ START -------------------------")
    for step in range(n_steps):
        action, _ = model.predict(obs, deterministic=True)
        sure_action = [[1, 1]]
        empty_action = [[0, 0]]
        random_action = [[random.randint(0, 1) for i in range(2)]]
        print("Step {}".format(step + 1))
        print("Action: ", action)
        obs, reward, done, info = verbose_env.step(empty_action)
        verbose_env.render()
        print('obs =', obs, 'reward=', reward, 'done=', done)
        # env.render(mode='console')
        if done:
            # Note that the VecEnv resets automatically
            # when a done signal is encountered
            print("Goal reached!", "reward=", reward)
            break
