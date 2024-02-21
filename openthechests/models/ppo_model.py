from stable_baselines3 import PPO


def get_model(env, verbose):
    return PPO('MultiInputPolicy', env, verbose=verbose)