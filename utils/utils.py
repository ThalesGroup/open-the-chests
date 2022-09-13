import re
import random

import numpy as np
import yaml
from numpy import mean, std


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


def parse_yaml_file(filename):
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


def read_yaml(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)


def my_evaluate(env, model, steps=100):
    rewards = []
    actions = []
    obs = env.reset()
    for i in range(steps):
        action, _ = model.predict(obs, deterministic=True)
        new_obs, reward, done, info = env.step(action)
        obs=new_obs
        if type(reward)!= int:
            print("BIGBIG PROBLEM STOPSTOP")
        rewards.append(reward)
        actions.append(action)
        if done:
            break
    return sum(rewards), rewards, actions, i


def my_evaluate_isolate(env, model, evaluated_box=0, steps=100):
    rewards = []
    actions = []
    active = []
    obs = env.reset()
    for i in range(steps):
        action, _ = model.predict(obs, deterministic=True)
        new_obs, reward, done, info = env.step(action)
        done = new_obs["open"][evaluated_box]
        reward = 0 if obs["active"][evaluated_box] else -1
        reward += -1 if action[evaluated_box] and not new_obs["open"][evaluated_box] else 0
        active.append(obs["active"][evaluated_box])
        obs = new_obs
        if type(reward) != int:
            print("BIGBIG PROBLEM STOPSTOP")
        rewards.append(reward)
        actions.append(action[evaluated_box])
        if done:
            break
    return sum(rewards), rewards, actions, active, i


def evaluate_multiple_times_isolate(env, model, repeats=10):
    rewards = []
    best_rewards = None
    best_actions = None
    best_steps = None
    for i in range(repeats):
        sum_reward, per_step_rewards, actions, actives, steps = my_evaluate_isolate(env, model, evaluated_box=0, steps=20)
        rewards.append(sum_reward)
        if max(rewards) <= sum_reward:
            best_actions = actions
            best_rewards = per_step_rewards
            best_steps = steps
    return mean(rewards), std(rewards), rewards, best_rewards, best_actions, best_steps
