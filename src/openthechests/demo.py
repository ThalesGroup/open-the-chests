import random

import plotly.io as pio
from stable_baselines3 import DQN

from src.openthechests.globals import ENV_CONFIG_FOLDER
from src.openthechests.env.OpenTheChestsGym import BoxEventEnv

pio.renderers.default = "browser"


# TODO (priority 2) add seed to environment

if __name__ == '__main__':
    # conf = "multiple_per_box.yaml"
    # conf = "one_distinct_per_box.yaml"
    # conf = "noise_one_per_box.yaml"
    conf = "one_per_box.yaml"
    env = BoxEventEnv.from_config_file("../../configs/" + conf, False)
    discrete_env = BoxEventEnv.from_config_file("../../configs/" + conf, False, discrete=True)
    verbose_env = BoxEventEnv.from_config_file("../../configs/" + conf, True)

    print("Learning")
    model = DQN('MultiInputPolicy', discrete_env, verbose=1).learn(10)

    n_steps = 200

    print("------------------------ START -------------------------")
    obs = env.reset()
    env.render()

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
        obs, reward, done, info = env.step(random_action)
        env.render()
        # print('obs =', obs, 'reward=', reward, 'done=', done)
        if done:
            # Note that the VecEnv resets automatically
            # when a done signal is encountered
            print("Goal reached!", "reward=", reward)
            break
    print("here")
    print(counter)
