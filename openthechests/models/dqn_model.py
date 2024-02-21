from stable_baselines3 import DQN


def get_model(env, verbose):
    return DQN('MultiInputPolicy', env, verbose=verbose)