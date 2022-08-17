import os
import shutil

from sb3_contrib import TRPO
from stable_baselines3.common.monitor import Monitor
from torch import nn

from stable_baselines3 import A2C, PPO
from stable_baselines3.common.env_util import make_vec_env

from globals import ENV_CONFIG_FOLDER, EXCOG_EXP_FOLDER
from mygym.BoxEventEnv import BoxEventEnv


def A2C_process(gamma,
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

    env = BoxEventEnv.from_config_file(ENV_CONFIG_FOLDER + "config.yaml", False)

    log_dir = EXCOG_EXP_FOLDER + monitor_file
    if os.path.exists(log_dir):
        shutil.rmtree(log_dir)
    os.makedirs(log_dir)

    env = Monitor(env, log_dir)

    net_arch = {
        "small": [dict(pi=[64, 64], vf=[64, 64])],
        "medium": [dict(pi=[256, 256], vf=[256, 256])],
    }[net_arch]
    activation_fn = {"tanh": nn.Tanh,
                     "relu": nn.ReLU,
                     "elu": nn.ELU,
                     "leaky_relu": nn.LeakyReLU
                     }[activation_fn]

    model = A2C('MultiInputPolicy', env,
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
    return {"mean_reward": 0,
            "std_reward": 0}


def PPO_process(batch_size,
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
    env = BoxEventEnv.from_config_file(ENV_CONFIG_FOLDER + "config.yaml", False)

    log_dir = EXCOG_EXP_FOLDER + monitor_file
    if os.path.exists(log_dir):
        shutil.rmtree(log_dir)
    os.makedirs(log_dir)

    env = Monitor(env, log_dir)

    net_arch = {
        "small": [dict(pi=[64, 64], vf=[64, 64])],
        "medium": [dict(pi=[256, 256], vf=[256, 256])],
    }[net_arch]

    activation_fn = {"tanh": nn.Tanh, "relu": nn.ReLU, "elu": nn.ELU, "leaky_relu": nn.LeakyReLU}[activation_fn]

    model = PPO('MultiInputPolicy', env,
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

    return {"mean_reward": 0, "std_reward": 0}


def TRPO_process(batch_size,
                 n_steps,
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
    env = BoxEventEnv.from_config_file(ENV_CONFIG_FOLDER + "config.yaml", False)

    log_dir = EXCOG_EXP_FOLDER + monitor_file
    if os.path.exists(log_dir):
        shutil.rmtree(log_dir)
    os.makedirs(log_dir)

    env = Monitor(env, log_dir)

    net_arch = {
        "small": [dict(pi=[64, 64], vf=[64, 64])],
        "medium": [dict(pi=[256, 256], vf=[256, 256])],
    }[net_arch]

    activation_fn = {"tanh": nn.Tanh, "relu": nn.ReLU, "elu": nn.ELU, "leaky_relu": nn.LeakyReLU}[activation_fn]

    model = TRPO('MultiInputPolicy', env,
                 batch_size=batch_size,
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

    model.learn(10000)

    return {"mean_reward": 0, "std_reward": 0}
