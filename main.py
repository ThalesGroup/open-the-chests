import argparse

from stable_baselines3.common import results_plotter
from stable_baselines3.common.monitor import Monitor
from src.BoxEventEnv import BoxEventEnv
from models import a2c_model, dqn_model, ppo_model, trpo_model

available_models = ["A2C", "DQN", "PPO", "TRPO"]

parser = argparse.ArgumentParser(description='Run a demo using a environment loaded via a configuration folder.')
parser.add_argument('--env_config', type=str, default='one_per_box.yaml',
                    help='The name of configuration file that defines an environment configuration.')
parser.add_argument("--discrete", type=bool, default=False,
                    help='Use discrete action input instead of a vector of binary values.')
parser.add_argument("--model", type=str, default="TRPO",
                    help=f'Model used to train on the environment. Current options : {available_models}')
parser.add_argument("--verbose_train", type=bool, default=True,
                    help='Use verbose mode when training model to get feedback.')
parser.add_argument("--train_steps", type=int, default=100000,
                    help="Number of steps to train model.")
parser.add_argument("--plot_training", type=bool, default=True,
                    help="Plot reward per step after training.")

if __name__ == '__main__':
    args = parser.parse_args()
    print(args)

    # get config from parser
    conf = args.env_config
    assert conf.split(".")[-1] == "yaml", f"Config file {conf} must be yaml file."
    # load environment from config
    """
    ATTENTION! 
    Pattern instructions must be in the same place as main yaml.
    The instructions must be in a folder with the same name.
    """
    discrete = args.discrete
    env = BoxEventEnv.from_config_file("./config/" + conf,
                                       verbose=False,
                                       discrete=discrete)

    # wrap env with monitor wrapper to track training
    env = Monitor(env, "./results/")

    # get model to use for training
    model_name = args.model
    verbose_train = args.verbose_train
    assert model_name in available_models, \
        f"The selected model must be from the list {available_models}"

    # load model depending on selection
    if model_name == "A2C":
        model = a2c_model.get_model(env=env, verbose=verbose_train)
    elif model_name == "DQN":
        assert discrete, "DQN model accepts only discrete actions, please set discrete parameter to True."
        model = dqn_model.get_model(env=env, verbose=verbose_train)
    elif model_name == "TRPO":
        model = trpo_model.get_model(env=env, verbose=verbose_train)
    elif model_name == "PPO":
        model = ppo_model.get_model(env=env, verbose=verbose_train)

    # get train steps
    train_steps = args.train_steps
    model.learn(train_steps)

    # plot results of training
    if args.plot_training:
        results_plotter.plot_results(["./results/"], 1e5, results_plotter.X_TIMESTEPS,
                                     "Reward per time-step")
