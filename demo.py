import random

import plotly.io as pio
from stable_baselines3 import DQN

from stable_baselines3.common.monitor import Monitor

from excog_experiments.Process import param_prepare
from globals import ENV_CONFIG_FOLDER
from src.BoxEventEnv import BoxEventEnv

pio.renderers.default = "browser"


# TODO (priority 2) add seed to environment

if __name__ == '__main__':
    # conf = "multiple_per_box.yaml"
    # conf = "one_distinct_per_box.yaml"
    # conf = "noise_one_per_box.yaml"
    conf = "one_per_box.yaml"
    env = BoxEventEnv.from_config_file(ENV_CONFIG_FOLDER + conf, False)
    discrete_env = BoxEventEnv.from_config_file(ENV_CONFIG_FOLDER + conf, False, discrete=True)
    verbose_env = BoxEventEnv.from_config_file(ENV_CONFIG_FOLDER + conf, True)

    print("Learning")
    model = DQN('MultiInputPolicy', discrete_env, verbose=1).learn(100000)

    n_steps = 200

    print("------------------------ START -------------------------")
    obs = discrete_env.reset()
    discrete_env.render()

    counter = 0
    for step in range(n_steps):
        counter += 1
        action, _ = model.predict(obs, deterministic=True)
        num_boxes = verbose_env.env.num_boxes
        sure_action = [1] * num_boxes
        empty_action = [0] * num_boxes
        random_action = [[random.randint(0, 1) for i in range(num_boxes)]]
        # print("Step {}".format(step + 1))
        # print("Action: ", action)
        obs, reward, done, info = discrete_env.step(action)
        discrete_env.render()
        # print('obs =', obs, 'reward=', reward, 'done=', done)
        if done:
            # Note that the VecEnv resets automatically
            # when a done signal is encountered
            print("Goal reached!", "reward=", reward)
            break
    print("here")
    print(counter)
