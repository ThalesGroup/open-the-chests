import re

import numpy as np
import yaml

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


def split_strip(s, c):
    return list(map(str.strip, s.split(c)))


def params_to_dict(s):
    if s == "{}":
        return dict()
    s = s.strip("{").strip("}").strip(" ")
    s = split_strip(s, ",")
    d = {split_strip(t, ":")[0]: split_strip(t, ":")[1] for t in s}
    return d


# TODO (priority 2) add safety for adding random white spaces
def line_to_command_dict(line: list[str]):
    if "delay" in line:
        delay_val_ind = line.index("delay") + 1
        return {"command": "delay", "parameters": int(line[delay_val_ind])}
    elif "instantiate" in line:
        instantiate_ind = line.index("instantiate")
        var_name = line[instantiate_ind + 1]
        event_info = line[instantiate_ind + 2]
        event_type = event_info[0]
        event_params = params_to_dict(event_info[1:])
        if "duration" in line:
            duration_ind = line.index("duration")
            duration_params = tuple(map(int, re.findall(r'[0-9]+', line[duration_ind + 1])))
            return event_type, event_params, duration_params
        return event_type, event_params

    elif "allen" in line:
        pass
