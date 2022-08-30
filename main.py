import random

import plotly.io as pio
from sb3_contrib import TRPO
from stable_baselines3 import A2C
from stable_baselines3.common.env_util import make_vec_env

from stable_baselines3.common.monitor import Monitor

from excog_experiments.Process import evaluate_multiple_times, param_prepare, load_env_monitor
from globals import ENV_CONFIG_FOLDER, EXCOG_EXP_FOLDER
from mygym.BoxEventEnv import BoxEventEnv
from utils.utils import bug_print

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

# TODO (priority 2) add seed to environment

if __name__ == '__main__':
    conf = "multiple_per_box.yaml"
    # conf = "one_distinct_per_box.yaml"
    # conf = "one_per_box.yaml"
    env = BoxEventEnv.from_config_file(ENV_CONFIG_FOLDER + conf, False)
    verbose_env = BoxEventEnv.from_config_file(ENV_CONFIG_FOLDER + conf, True)

    env = Monitor(env, ".")
    verbose_env = Monitor(verbose_env, ".")

    env = load_env_monitor(["multiple_per_box.yaml"], "deletethis")

    # Train the agent
    print("Learning")

    params = {'batch_size': 64.0,
              'n_critic_updates': 25.0,
              'cg_max_steps': 25.0,
              'target_kl': 0.005,
              'gamma': 0.98,
              'gae_lambda': 0.8,
              'n_steps': 64,
              'learning_rate': 0.5039112109375,
              'net_arch': 'small',
              'activation_fn': 'tanh',
              'seed': 42}

    activation_fn, learning_rate, net_arch = param_prepare(params["activation_fn"], params["learning_rate"], params["net_arch"])

    model = TRPO('MultiInputPolicy', env, verbose=1,
                 batch_size=params["batch_size"],
                 seed=params["seed"],
                 n_steps=params["n_steps"],
                 gamma=params["gamma"],
                 learning_rate=learning_rate,
                 n_critic_updates=params["n_critic_updates"],
                 cg_max_steps=params["cg_max_steps"],
                 target_kl=params["target_kl"],
                 gae_lambda=params["gae_lambda"],
                 policy_kwargs=dict(
                     net_arch=net_arch,
                     ortho_init=0.5,
                     activation_fn=activation_fn)
                 )

    model.learn(10000)

    print("Evaluating")
    # TODO (priority 1) give timeout to avoid infinite run
    # print(evaluate_policy(model, verbose_env, n_eval_episodes=2))

    # model = A2C('MultiInputPolicy', env, verbose=1).learn(10000)
    # model = A2C('MultiInputPolicy', env, verbose=1)

    # Test the trained agent

    n_steps = 100
    print("------------------------ START -------------------------")
    obs = verbose_env.reset()
    verbose_env.render()

    counter = 0
    for step in range(n_steps):
        counter += 1
        action, _ = model.predict(obs, deterministic=True)
        num_boxes = env.env.num_boxes
        sure_action = [1] * num_boxes
        empty_action = [0] * num_boxes
        random_action = [[random.randint(0, 1) for i in range(num_boxes)]]
        print("Step {}".format(step + 1))
        print("Action: ", action)
        obs, reward, done, info = verbose_env.step(random_action)
        verbose_env.render()
        print('obs =', obs, 'reward=', reward, 'done=', done)
        if done:
            # Note that the VecEnv resets automatically
            # when a done signal is encountered
            print("Goal reached!", "reward=", reward)
            break
    print(counter)
