from numpy import mean, std


def evaluate_multiple_times(env, model, repeats=10):
    """
    Evaluate a model on an environment multiple times and return statistics over all evaluations.
    Returned information :
        - The average cumulated reward over all evaluations
        - The standard deviation of cumulated rewards over all evaluations
        - The list of obtained cumulated rewards for every evaluation
        - The rewards per step obtained by the best evaluation
        - The actions made per step of the best evaluation
        - The number of steps of the best evaluation

    :param env: The environment used for evaluation.
    :param model: The model to evaluate.
    :param repeats: Number of times to repeat evaluation.
    :return: Statistics over evaluations.
    """
    sum_rewards = []
    best_eval_rewards = None
    best_eval_actions = None
    best_eval_steps = None
    for i in range(repeats):
        sum_reward, per_step_rewards, actions, steps = evaluate_one_episode(env, model)
        sum_rewards.append(sum_reward)
        # if this is the best achieved reward, keep the eval history
        if max(sum_rewards) <= sum_reward:
            best_eval_actions = actions
            best_eval_rewards = per_step_rewards
            best_eval_steps = steps
    return mean(sum_rewards), std(sum_rewards), sum_rewards, \
           best_eval_rewards, best_eval_actions, best_eval_steps


def evaluate_one_episode(env, model):
    """
    Evaluate a model on an environment for one episode.
    Track rewards and return:
        - the cumulated rewards over the episode
        - the list of reward per step
        - the list of action per step
        - the number of steps

    :param env: The environment used for evaluation.
    :param model: The model to evaluate.
    :return: The cumulated reward, reward per step, action per step, number of steps
    """
    rewards = []
    actions = []
    steps = 0
    done = False
    obs = env.reset()
    while not done:
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, done, info = env.step(action)
        rewards.append(reward)
        actions.append(action)
        steps += 1
    return sum(rewards), rewards, actions, steps


def my_evaluate_isolate(env, model, evaluated_box=0, steps=100):
    rewards = []
    actions = []
    active = []
    obs = env.reset()
    for i in range(steps):
        action, _ = model.predict(obs, deterministic=True)
        new_obs, reward, done, info = env.step(action)
        done = new_obs["_open"][evaluated_box]
        reward = 0 if obs["active"][evaluated_box] else -1
        reward += -1 if action[evaluated_box] and not new_obs["_open"][evaluated_box] else 0
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
