import random

import numpy as np
import yaml


def bug_print(something="", msg=""):
    print("################################")
    print(msg)
    print(something)
    print("################################")


def boxes_to_discrete(num_boxes):
    """
    Produce a discrete number that represents all possible box states, where each box state is represented by a binary
    number of size equal to the number of boxes.
    Example:  Two boxes can be represented as a binary vector of size two.
    All possible states include 00, 01, 10, 11 represented by 2**2 = 4 possible combinations.

    :param num_boxes:
    :return:
    """
    return 2 ** num_boxes


def my_normal(mu, sigma):
    """
    Clipped normal distribution that makes sure no negative _time durations are generated.
    :param mu: Mean used for normal distribution.
    :param sigma: Variance used for normal distribution.
    :return: A sampled duration of minimal value (mu - sigma) and maximal value (mu + sigma.
    """
    assert mu - sigma >= 0, "Allows negative _time durations"
    res = random.normalvariate(mu, sigma)
    res = max((mu - sigma), res)
    res = min((mu + sigma), res)
    return res


# TODO (priority 3) can this be more general?
def to_stb3_obs_format(obs: dict):
    """
    Stable Baselines 3 only accepts observation output formats under the form of one level dictionaries.
    Since the standard environment output is under the form of a multi level dictionary containing object,
    we use this function to transform it into an acceptable formatting.

    :param obs: Observation to be transformed.
    :return: One level dictionary representing the observation.
    """
    final_dict = dict()
    for key, value in obs.items():
        if key == "state":
            for state_key, state_value in obs[key].items():
                obs[key][state_key] = np.array([int(xi) for xi in obs[key][state_key]])
        elif key == "context":
            event_dict = obs[key].to_dict()
            for event_time_key in ["start", "end", "duration"]:
                event_dict[event_time_key] = np.array(event_dict[event_time_key]).reshape(-1)
            obs[key] = event_dict

        if type(obs[key]) == dict:
            final_dict = final_dict | obs[key]
        else:
            final_dict[key] = obs[key]
    return final_dict


def parse_yaml_file(filename):
    """
    Allows to parse a YAML file of instructions and transform it into a list of dictionaries that is accepted by the environment.

    :param filename: The YAML file to parse.
    :return: The produced instructions.
    """
    instructions = []
    with open(filename, "r") as f:
        conf = yaml.safe_load(f)
    instructions.append({"command": "delay", "parameters": conf["GENERAL"]["delay"]})
    instructions.append({"command": "noise", "parameters": conf["GENERAL"]["noise"]})
    for event in conf["INSTANTIATE"]:
        attr = event["params"] if "params" in event else {}
        duration_dist = {"mu": event["duration"]["mu"],
                         "sigma": event["duration"]["sigma"]} if "duration" in event else None
        instr = {"command": "instantiate",
                 "parameters": (event["type"], attr, duration_dist),
                 "variable_name": event["name"]}
        instructions.append(instr)
    if "RELATIONSHIP" in conf:
        for relation in conf["RELATIONSHIP"]:
            other_params = relation["other"] if "other" in relation else {}
            instr = {"command": relation["type"],
                     "parameters": relation["events"],
                     "variable_name": relation["events"][0],
                     "other": other_params}
            instructions.append(instr)
    return instructions
