import argparse
import os

from stable_baselines3.common import results_plotter
from stable_baselines3.common.monitor import Monitor
from src.BoxEventEnv import BoxEventEnv
from models import a2c_model, dqn_model, ppo_model, trpo_model
from src.utils.evaluators import evaluate_multiple_times

available_models = ["A2C", "DQN", "PPO", "TRPO"]

parser = argparse.ArgumentParser(description='Run a demo using a environment loaded via a configuration folder.')

parser.add_argument('--env_config', type=str, default='one_per_box.yaml',
                    help='The name of configuration file that defines an environment configuration.')

parser.add_argument("--discrete", type=bool, default=False,
                    help='Use discrete action input instead of a vector of binary values.')

parser.add_argument("--model", type=str, default="PPO",
                    help=f'Model used to train on the environment. Current options : {available_models}')

parser.add_argument("--verbose_train", type=bool, default=False,
                    help='Use verbose mode when training model to get feedback.')

parser.add_argument("--train_steps", type=int, default=100000,
                    help="Number of steps to train model.")

parser.add_argument("--plot_training", type=bool, default=True,
                    help="Plot reward per step after training.")

parser.add_argument("--num_episodes_eval", type=int, default=100,
                    help="Number of episodes over which to evaluate environment.")

parser.add_argument("--show_one_episode", type=bool, default=False,
                    help="Render one episode play trough using the trained model.")

parser.add_argument("--results_file", type=str, default="results",
                    help="Render one episode play trough using the trained model.")


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

    # get model to use for training
    verbose_train = args.verbose_train
    model_name = args.model
    assert model_name in available_models, \
        f"The selected model must be from the list {available_models}"

    # wrap env with monitor wrapper to track training
    os.makedirs(f"./{args.results_file}/{model_name}/{conf.split('.')[0]}/", 0o7770)
    env = Monitor(env, f"./{args.results_file}/{model_name}/{conf.split('.')[0]}/")

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
        results_plotter.plot_results([f"./{args.results_file}/{model_name}/{conf.split('.')[0]}/"], 1e5, results_plotter.X_TIMESTEPS,
                                     "Reward per time-step")

    env.reset()
    mean_cumulated_reward, std_cumulated_reward, sum_rewards, best_eval_rewards, best_eval_actions, best_eval_steps = \
        evaluate_multiple_times(env=env, model=model, repeats=args.num_episodes_eval)

    print(f"Over {args.num_episodes_eval} episode evaluations")
    print("==================================================")
    print(f"Mean cumulated reward: {mean_cumulated_reward}")
    print(f"Standard deviation of the cumulated reward: {std_cumulated_reward}")
    print(f"All obtained cumulated rewards: {sum_rewards}")
    print(f"Best evaluation rewards per step: {best_eval_rewards}")
    print(f"Best evaluation actions per step: {best_eval_actions}")
    print(f"Best evaluation number of steps: {best_eval_steps}")

    import pickle

    with open(f"./{args.results_file}/{model_name}/{conf.split('.')[0]}/outfile", 'wb') as fp:
        pickle.dump(mean_cumulated_reward, fp)
        pickle.dump(std_cumulated_reward, fp)
        pickle.dump(sum_rewards, fp)
        pickle.dump(best_eval_rewards, fp)
        pickle.dump(best_eval_steps, fp)

    if args.show_one_episode:
        done = False
        obs = env.reset()
        env.render()
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, done, info = env.step(action)
            env.render()
