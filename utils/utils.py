import numpy as np

from Elements.Event import Event


def bug_print(something, msg):
    print("################################")
    print(msg)
    print(something)
    print("################################")


def list_to_labels(l):
    return [i for i in range(len(l))]


def process_obs(obs: dict):
    final_dict = dict()
    for key, value in obs.items():
        if type(value) == dict:
            final_dict = final_dict | value
        elif type(value) == Event:
            final_dict = final_dict | value.to_dict()
        else:
            final_dict[key] = value

    for key, value in final_dict.items():
        # TODO (priority 2) total workaround must fix
        if key not in ["e_type", "fg", "bg"]:
            final_dict[key] = np.array(value)
            if key in ["start", "end", "duration"]:
                final_dict[key] = final_dict[key].reshape(-1)
            if key in ["open", "active"]:
                final_dict[key] = np.array([int(xi) for xi in final_dict[key]])
    return final_dict
