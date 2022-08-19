import os
import shutil

import numpy as np
from numpy import mean, std
from sb3_contrib import TRPO
from stable_baselines3.common.monitor import Monitor
from torch import nn

from stable_baselines3 import A2C, PPO
from stable_baselines3.common.env_util import make_vec_env

from globals import ENV_CONFIG_FOLDER, EXCOG_EXP_FOLDER
from mygym.BoxEventEnv import BoxEventEnv
from utils.utils import bug_print, my_evaluate


def load_env_monitor(data1, monitor_file):
    print(data1[0])
    env = BoxEventEnv.from_config_file(ENV_CONFIG_FOLDER + data1[0], False)
    log_dir = EXCOG_EXP_FOLDER + monitor_file
    if os.path.exists(log_dir):
        shutil.rmtree(log_dir)
    os.makedirs(log_dir)
    env = Monitor(env, log_dir)
    return env


def param_prepare(activation_fn, learning_rate, net_arch):
    net_arch = {
        "small": [dict(pi=[64, 64], vf=[64, 64])],
        "medium": [dict(pi=[256, 256], vf=[256, 256])],
    }[net_arch]
    activation_fn = {"tanh": nn.Tanh, "relu": nn.ReLU, "elu": nn.ELU, "leaky_relu": nn.LeakyReLU}[activation_fn]
    learning_rate = np.exp(learning_rate)
    return activation_fn, learning_rate, net_arch


def evaluate_multiple_times(env, model, repeats=10):
    rewards = []
    best_rewards = None
    best_actions = None
    best_steps = None
    for i in range(repeats):
        sum_reward, per_step_rewards, actions, steps = my_evaluate(env, model, 200)
        rewards.append(sum_reward)
        if max(rewards) <= sum_reward:
            best_actions = actions
            best_rewards = per_step_rewards
            best_steps = steps
    return mean(rewards), std(rewards), rewards, best_rewards, best_actions, best_steps


def A2C_process(gamma,
                seed,
                normalize_advantage,
                max_grad_norm,
                use_rms_prop,
                gae_lambda,
                n_steps,
                learning_rate,
                ent_coef,
                vf_coef,
                ortho_init,
                net_arch,
                activation_fn,
                data1,
                monitor_file, **kwargs):
    print("A2C")
    env = load_env_monitor(data1, monitor_file)

    activation_fn, learning_rate, net_arch = param_prepare(activation_fn, learning_rate, net_arch)
    ent_coef = np.exp(ent_coef)

    model = A2C('MultiInputPolicy', env,
                seed=seed,
                gamma=gamma,
                normalize_advantage=normalize_advantage,
                max_grad_norm=max_grad_norm,
                use_rms_prop=use_rms_prop,
                gae_lambda=gae_lambda,
                n_steps=n_steps,
                learning_rate=learning_rate,
                ent_coef=ent_coef,
                vf_coef=vf_coef,
                policy_kwargs=dict(ortho_init=ortho_init,
                                   net_arch=net_arch,
                                   activation_fn=activation_fn)
                )
    model.learn(10000)

    mean_rewards, std_rewards, rewards, best_rewards, best_actions, best_steps = evaluate_multiple_times(env, model)

    return {"method": "A2C",
            "mean_reward": mean_rewards,
            "std_reward": std_rewards,
            "all_trials_rewards": rewards,
            "best_trial_par_step_rewards": best_rewards,
            "best_trial_par_step_actions": best_actions,
            "best_trial_par_step_steps": best_steps}


def PPO_process(batch_size,
                seed,
                n_steps,
                gamma,
                learning_rate,
                ent_coef,
                clip_range,
                n_epochs,
                gae_lambda,
                max_grad_norm,
                vf_coef,
                net_arch,
                ortho_init,
                activation_fn,
                data1,
                monitor_file, **kwargs):
    #
    # Code that uses the arguments...
    #
    print("PPO")
    env = load_env_monitor(data1, monitor_file)

    activation_fn, learning_rate, net_arch = param_prepare(activation_fn, learning_rate, net_arch)
    ent_coef = np.exp(ent_coef)

    model = PPO('MultiInputPolicy', env,
                seed=seed,
                batch_size=batch_size,
                n_steps=n_steps,
                gamma=gamma,
                learning_rate=learning_rate,
                ent_coef=ent_coef,
                clip_range=clip_range,
                n_epochs=n_epochs,
                gae_lambda=gae_lambda,
                max_grad_norm=max_grad_norm,
                vf_coef=vf_coef,
                policy_kwargs=dict(
                    net_arch=net_arch,
                    ortho_init=ortho_init,
                    activation_fn=activation_fn)
                )

    model.learn(10000)

    mean_rewards, std_rewards, rewards, best_rewards, best_actions, best_steps = evaluate_multiple_times(env, model)

    return {"method": "PPO",
            "mean_reward": mean_rewards,
            "std_reward": std_rewards,
            "all_trials_rewards": rewards,
            "best_trial_par_step_rewards": best_rewards,
            "best_trial_par_step_actions": best_actions,
            "best_trial_par_step_steps": best_steps}


def TRPO_process(batch_size,
                 n_steps,
                 seed,
                 gamma,
                 learning_rate,
                 n_critic_updates,
                 cg_max_steps,
                 target_kl,
                 gae_lambda,
                 net_arch,
                 ortho_init,
                 activation_fn,
                 data1,
                 monitor_file, **kwargs):
    #
    # Code that uses the arguments...
    #
    print("TRPO")
    env = load_env_monitor(data1, monitor_file)

    activation_fn, learning_rate, net_arch = param_prepare(activation_fn, learning_rate, net_arch)

    model = TRPO('MultiInputPolicy', env,
                 batch_size=batch_size,
                 seed=seed,
                 n_steps=n_steps,
                 gamma=gamma,
                 learning_rate=learning_rate,
                 n_critic_updates=n_critic_updates,
                 cg_max_steps=cg_max_steps,
                 target_kl=target_kl,
                 gae_lambda=gae_lambda,
                 policy_kwargs=dict(
                     net_arch=net_arch,
                     ortho_init=ortho_init,
                     activation_fn=activation_fn)
                 )

    try:
        model.learn(10000)
        mean_rewards, std_rewards, rewards, best_rewards, best_actions, best_steps = evaluate_multiple_times(env, model)

        return {"method": "TRPO",
                "mean_reward": mean_rewards,
                "std_reward": std_rewards,
                "all_trials_rewards": rewards,
                "best_trial_par_step_rewards": best_rewards,
                "best_trial_par_step_actions": best_actions,
                "best_trial_num_step_steps": best_steps}

    except:
        return {"method": "TRPO",
                "mean_reward": "cant converge"}
