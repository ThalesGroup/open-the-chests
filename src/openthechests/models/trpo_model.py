from sb3_contrib import TRPO


def get_model(env, verbose):
    return TRPO('MultiInputPolicy', env, verbose=verbose)