from numpy import mean, std


def evaluate_multiple_times(env, model, repeats=10):
    rewards = []
    best_rewards = None
    best_actions = None
    best_steps = None
    for i in range(repeats):
        sum_reward, per_step_rewards, actions, steps = my_evaluate(env, model, 200)
        rewards.append(sum_reward)
        if max(rewards) <= sum_reward:
            best_actions = actions
            best_rewards = per_step_rewards
            best_steps = steps
    return mean(rewards), std(rewards), rewards, best_rewards, best_actions, best_steps


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