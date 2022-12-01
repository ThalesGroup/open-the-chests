# TODO Priority 1: clean up alm unneeded experiment files

import random
import plotly.io as pio
from stable_baselines3 import DQN

from src.openthechests.env.OpenTheChestsGym import OpenTheChestsGym
from src.openthechests.env.utils.helper_functions import bug_print

pio.renderers.default = "browser"


if __name__ == '__main__':
    # conf = "multiple_per_box.yaml"
    # conf = "one_distinct_per_box.yaml"
    # conf = "noise_one_per_box.yaml"
    conf = "one_per_box.yaml"
    env = OpenTheChestsGym.from_config_file(env_config_file="../../configs/" + conf,
                                            verbose=False)
    discrete_env = OpenTheChestsGym.from_config_file(env_config_file="../../configs/" + conf,
                                                     verbose=False,
                                                     discrete=True)
    verbose_env = OpenTheChestsGym.from_config_file(env_config_file="../../configs/" + conf,
                                                    verbose=True)

    print("Learning")
    model = DQN('MultiInputPolicy', discrete_env, verbose=1)

    n_steps = 200

    env = verbose_env

    print("------------------------ START -------------------------")
    obs = env.reset()
    env.render()

    counter = 0
    for step in range(n_steps):
        counter += 1
        action, _ = model.predict(obs, deterministic=True)
        num_boxes = env.env.get_num_boxes()
        sure_action = [1] * num_boxes
        empty_action = [0] * num_boxes
        random_action = [random.randint(0, 1) for i in range(num_boxes)]
        # print("Step {}".format(step + 1))
        # print("Action: ", action)
        obs, reward, done, info = env.step(empty_action)
        env.render()
        # print('obs =', obs, 'reward=', reward, 'done=', done)
        if done:
            # Note that the VecEnv resets automatically
            # when a done signal is encountered
            print("Goal reached!", "reward=", reward)
            break
    print("here")
    print(counter)
