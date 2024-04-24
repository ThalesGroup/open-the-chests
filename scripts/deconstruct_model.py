import plotly.io as pio
from sb3_contrib import TRPO
from stable_baselines3.common.monitor import Monitor
from excog_experiments.Process import param_prepare
from openthechests.env.OpenTheChestsGym import OpenTheChestsGym
from openthechests.env.utils.evaluators import evaluate_multiple_times, evaluate_multiple_times_isolate, \
    my_evaluate_isolate
from openthechests.env.utils.helper_functions import bug_print
from openthechests.globals import ENV_CONFIG_FOLDER

pio.renderers.default = "browser"

# TRAIN MODEL AND EVAL


conf = "multiple_per_box.yaml"
# conf = "one_distinct_per_box.yaml"
# conf = "one_per_box.yaml"
env = OpenTheChestsGym.from_config_file(ENV_CONFIG_FOLDER + conf, False)
verbose_env = OpenTheChestsGym.from_config_file(ENV_CONFIG_FOLDER + conf, True)

env = Monitor(env, "deletethis")
verbose_env = Monitor(verbose_env, "deletethis")

# Train the agent
print("Learning")

params = {'batch_size': 64,
          'n_critic_updates': 25,
          'cg_max_steps': 25,
          'target_kl': 0.005,
          'gamma': 0.98,
          'gae_lambda': 0.8,
          'n_steps': 64,
          'learning_rate': 0.5039112109375,
          'net_arch': 'small',
          'activation_fn': 'tanh',
          'seed': 42}

activation_fn, learning_rate, net_arch = param_prepare(params["activation_fn"], params["learning_rate"],
                                                       params["net_arch"])

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
bug_print(evaluate_multiple_times(env, model))

conf = "multiple_per_box_isolate.yaml"
first_env = OpenTheChestsGym.from_config_file(env_config_file=ENV_CONFIG_FOLDER + conf, verbose=False)

bug_print(evaluate_multiple_times_isolate(env, model))

bug_print(evaluate_multiple_times_isolate(first_env, model))

bug_print(my_evaluate_isolate(first_env, model, evaluated_box=0, steps=100))

