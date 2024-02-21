from stable_baselines3 import A2C


def get_model(env, verbose):
    return A2C('MultiInputPolicy', env, verbose=verbose)