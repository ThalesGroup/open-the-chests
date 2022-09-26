import random

import plotly.io as pio
from sb3_contrib import TRPO
from stable_baselines3 import A2C, DQN
from stable_baselines3.common.env_util import make_vec_env

from stable_baselines3.common.monitor import Monitor

from excog_experiments.Process import evaluate_multiple_times, param_prepare, load_env_monitor, TRPO_process
from globals import ENV_CONFIG_FOLDER, EXCOG_EXP_FOLDER
from mygym.BoxEventEnv import BoxEventEnv
from utils.utils import bug_print

pio.renderers.default = "browser"


# TODO (priority 2) add seed to environment

if __name__ == '__main__':
    # conf = "multiple_per_box.yaml"
    # conf = "one_distinct_per_box.yaml"
    conf = "one_per_box.yaml"
    env = BoxEventEnv.from_config_file(ENV_CONFIG_FOLDER + conf, False)
    discrete_env = BoxEventEnv.from_config_file(ENV_CONFIG_FOLDER + conf, True, True)
    verbose_env = BoxEventEnv.from_config_file(ENV_CONFIG_FOLDER + conf, True)

    # env = Monitor(env, "deletethis")
    # verbose_env = Monitor(verbose_env, "deletethis")

    # Train the agent
    print("Learning")

    # TRPO
    # params = {'batch_size': 64,
    #           'n_critic_updates': 25,
    #           'cg_max_steps': 25,
    #           'target_kl': 0.005,
    #           'gamma': 0.98,
    #           'gae_lambda': 0.8,
    #           'n_steps': 64,
    #           'learning_rate': 0.5039112109375,
    #           'net_arch': 'small',
    #           'activation_fn': 'tanh',
    #           'seed': 42}



    #A2C
    params = {'ent_coef': 0.011035165146484,
              "vf_coef" : 0.39404296875,
              "gamma" : 0.95,
              "gae_lambda" : 0.98,
              "n_steps": 2048,
              "learning_rate": 0.29883513671875,
              "net_arch" : "small",
              "activation_fn": "relu",
              "seed": 666,
              "normalize_advantage": True,
              "max_grad_norm": 0.3,
              "use_rms_prop": False
              }

    activation_fn, learning_rate, net_arch = param_prepare(params["activation_fn"], params["learning_rate"], params["net_arch"])
    for key in ["activation_fn", "learning_rate", "net_arch"]:
        params.pop(key)

    # model = TRPO('MultiInputPolicy', env, verbose=1,
    #              batch_size=params["batch_size"],
    #              seed=params["seed"],
    #              n_steps=params["n_steps"],
    #              gamma=params["gamma"],
    #              learning_rate=learning_rate,
    #              n_critic_updates=params["n_critic_updates"],
    #              cg_max_steps=params["cg_max_steps"],
    #              target_kl=params["target_kl"],
    #              gae_lambda=params["gae_lambda"],
    #              policy_kwargs=dict(
    #                  net_arch=net_arch,
    #                  ortho_init=0.5,
    #                  activation_fn=activation_fn)
    #              )
    #
    # model.learn(10000)
    #
    # bug_print(evaluate_multiple_times(env, model))

    print("Evaluating")
    # TODO (priority 1) give timeout to avoid infinite run
    # print(evaluate_policy(model, verbose_env, n_eval_episodes=2))

    # model = A2C('MultiInputPolicy', env, verbose=1,
    #             policy_kwargs=dict(
    #                 net_arch=net_arch,
    #                 ortho_init=0.5,
    #                 activation_fn=activation_fn),
    #             **params
    # ).learn(10000)

    print("here")
    model = DQN('MultiInputPolicy', discrete_env, verbose=1)#.learn(10000)
    print("here")

    # model = A2C('MultiInputPolicy', env, verbose=1)

    # Test the trained agent

    n_steps = 200
    # verbose_env = first_box_env
    print("------------------------ START -------------------------")
    obs = discrete_env.reset()
    discrete_env.render()

    counter = 0
    for step in range(n_steps):
        if counter == 5:
            discrete_env.reset()
        counter += 1
        action, _ = model.predict(obs, deterministic=True)
        num_boxes = verbose_env.env.num_boxes
        sure_action = [1] * num_boxes
        empty_action = [0] * num_boxes
        random_action = [[random.randint(0, 1) for i in range(num_boxes)]]
        print("Step {}".format(step + 1))
        print("Action: ", action)
        obs, reward, done, info = discrete_env.step(0)
        discrete_env.render()
        print('obs =', obs, 'reward=', reward, 'done=', done)
        if done:
            # Note that the VecEnv resets automatically
            # when a done signal is encountered
            print("Goal reached!", "reward=", reward)
            break
    print("here")
    print(counter)
