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
    """
    Clipped normal distribution that makes sure no negative time durations are generated.
    :param mu: Mean used for normal distribution.
    :param sigma: Variance used for normal distribution.
    :return: A sampled duration of minimal value (mu - sigma) and maximal value (mu + sigma.
    """
    assert mu - sigma >= 0, "Allows negative time durations"
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


def my_evaluate(env, model, steps=100):
    rewards = []
    actions = []
    obs = env.reset()
    for i in range(steps):
        action, _ = model.predict(obs, deterministic=True)
        new_obs, reward, done, info = env.step(action)
        obs = new_obs
        if type(reward) != int:
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
        sum_reward, per_step_rewards, actions, actives, steps = my_evaluate_isolate(env, model, evaluated_box=0,
                                                                                    steps=20)
        rewards.append(sum_reward)
        if max(rewards) <= sum_reward:
            best_actions = actions
            best_rewards = per_step_rewards
            best_steps = steps
    return mean(rewards), std(rewards), rewards, best_rewards, best_actions, best_steps
