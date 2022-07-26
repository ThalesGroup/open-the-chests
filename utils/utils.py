import re
import random

import numpy as np
import yaml

from Elements.Event import Event


def bug_print(something="", msg=""):
    print("################################")
    print(msg)
    print(something)
    print("################################")


def my_normal(mu, sigma):
    assert mu - sigma >= 0, "Allows negative time durations"
    res = random.normalvariate(mu, sigma)
    res = max((mu - sigma), res)
    res = min((mu + sigma), res)
    return res


def list_to_labels(l):
    return [i for i in range(len(l))]


# TODO (priority 3) can this be more general?
def process_obs(obs: dict):
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


def split_strip(s, c):
    return list(map(str.strip, s.split(c)))


def params_to_dict(s):
    if s == "{}":
        return dict()
    s = s.strip("{").strip("}").strip(" ")
    s = split_strip(s, ",")
    d = {split_strip(t, ":")[0]: split_strip(t, ":")[1] for t in s}
    return d


def parse_tuple(s):
    return tuple(map(int, re.findall(r'[0-9]+', s)))


# instr1 = [{"command": "delay", "parameters": 5},
#           {"command": "instantiate", "parameters": ("A", {"bg": "blue"}, (4, 2)), "variable_name": "a1"},
#           {"command": "instantiate", "parameters": ("C", {"fg": "red"}, (10, 1)), "variable_name": "c1"},
#           {"command": "after", "parameters": ("c1", "a1"), "variable_name": "c1", "other": {"gap_dist": (2, 1)}},
#           {"command": "instantiate", "parameters": ("C", {}, (4, 1)), "variable_name": "c2"},
#           {"command": "during", "parameters": ("c2", "c1"), "variable_name": "c2"},
#           {"command": "instantiate", "parameters": ("A", {}), "variable_name": "a2"},
#           {"command": "met_by", "parameters": ("a2", "c1"), "variable_name": "a2"}]
#
# instr2 = [{"command": "delay", "parameters": 7},
#           {"command": "instantiate", "parameters": ("B", {"bg": "blue"}, (4, 2)), "variable_name": "b1"},
#           {"command": "instantiate", "parameters": ("B", {"fg": "red"}, (10, 1)), "variable_name": "b2"},
#           {"command": "after", "parameters": ("b2", "b1"), "variable_name": "b2", "other": {"gap_dist": (2, 1)}}]
#


# TODO (priority 2) add safety for adding random white spaces
def line_to_command_dict(line: str):
    line = line.split(" ")
    if "delay" in line:
        delay_val_ind = line.index("delay") + 1
        return {"command": "delay", "parameters": int(line[delay_val_ind])}

    elif "noise" in line:
        noise_val_ind = line.index("noise") + 1
        return {"command": "noise", "parameters": float(line[noise_val_ind])}

    elif "instantiate" in line:
        instantiate_ind = line.index("instantiate")
        var_name = line[instantiate_ind + 1]
        event_info = line[instantiate_ind + 2]
        event_type = event_info[0]
        event_params = params_to_dict(event_info[1:])
        if "duration" in line:
            duration_ind = line.index("duration")
            duration_params = parse_tuple(line[duration_ind + 1])
            return {"command": "instantiate", "parameters": (event_type, event_params, duration_params),
                    "variable_name": var_name}
        return {"command": "instantiate", "parameters": (event_type, event_params), "variable_name": var_name}

    elif "allen" in line:
        allen_ind = line.index("allen")
        allen_op = line[allen_ind + 1]
        e1 = line[allen_ind - 1]
        e2 = line[allen_ind + 2]
        if len(line) > 4:
            other_params = dict()
            for i in range(4, len(line), 2):
                other_params[line[i]] = parse_tuple(line[i + 1])
            return {"command": allen_op, "parameters": (e1, e2), "variable_name": e1, "other": other_params}
        # TODO (priority 2) is variable name necessary and what is its place
        return {"command": allen_op, "parameters": (e1, e2), "variable_name": e1}


def parse_file(filename):
    with open(filename) as f:
        lines = [line.rstrip() for line in f]
    return list(map(line_to_command_dict, lines))


def read_yaml(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)
