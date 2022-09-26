"""
OUTDATED (Keeping for future needs)
Past code used for parsing string file of commands.
"""


import re


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
            return {"command": "instantiate",
                    "parameters": (event_type, event_params, duration_params),
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