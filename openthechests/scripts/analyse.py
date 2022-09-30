import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.lines as mlines
import matplotlib.transforms as mtransforms

new_results = pd.read_csv("/home/S3G-LABS/u1226/data/excog_results_couple_noise/0/results.csv")
results = pd.read_csv("/home/S3G-LABS/u1226/data/excog_results/0/results.csv")

full_results = pd.concat([results, new_results], ignore_index=True, sort=False)
new_results.loc[new_results["method"] != "TRPO", "best_trial_num_step_steps"] = \
    new_results[new_results["method"] != "TRPO"]["best_trial_par_step_steps"]

new_results["mean_reward"] = new_results["mean_reward"].replace(["cant converge"], [None])
new_results["mean_reward"] = pd.to_numeric(new_results["mean_reward"], errors='coerce')

new_results["mean_reward"] = new_results["mean_reward"].replace(["cant converge"], [None])
new_results["mean_reward"] = pd.to_numeric(new_results["mean_reward"], errors='coerce')

new_agg = new_results.groupby(["method", "data1"]).agg(
    {"mean_reward": ["max", "mean", "std"], "best_trial_num_step_steps": ["min", "mean", "std"]})

full_results.loc[full_results["method"] != "TRPO", "best_trial_num_step_steps"] = \
    full_results[full_results["method"] != "TRPO"]["best_trial_par_step_steps"]
full_results["mean_reward"] = full_results["mean_reward"].replace(["cant converge"], [None])
full_results["mean_reward"] = pd.to_numeric(full_results["mean_reward"], errors='coerce')

new_agg = full_results.groupby(["method", "data1"]).agg(
    {"mean_reward": ["max", "mean", "std"], "best_trial_num_step_steps": ["min", "mean", "std"]})

best_mean_reward = full_results.loc[
    full_results.groupby(["method", "data1"])['mean_reward'].idxmax().reset_index()["mean_reward"]]
best_num_steps = full_results.loc[
    full_results.groupby(["method", "data1"])['best_trial_num_step_steps'].idxmin().reset_index()[
        "best_trial_num_step_steps"]]

multiple_TRPO_params = best_mean_reward.loc[
    (best_mean_reward['method'] == "TRPO") & (best_mean_reward['data1'] == "multiple_per_box.yaml")].dropna(axis=1,
                                                                                                            how='all')
multiple_TRPO_params = multiple_TRPO_params[['batch_size', 'n_critic_updates', 'cg_max_steps',
                                             'target_kl', 'gamma', 'gae_lambda', 'n_steps', 'learning_rate',
                                             'net_arch', 'activation_fn', 'seed']]

multiple_TRPO_params_dict = multiple_TRPO_params.reset_index().loc[0].to_dict()

# VISUALISE HERE

grouped = full_results[["method", "data1", "mean_reward"]].groupby(["method", "data1"])

grouped_keys = list(grouped.groups.keys())

one = sorted([t for t in grouped_keys if t[1] == "one_per_box.yaml"], key=lambda x: x[0])
two = sorted([t for t in grouped_keys if t[1] == "one_distinct_per_box.yaml"], key=lambda x: x[0])
three = sorted([t for t in grouped_keys if t[1] == "multiple_per_box.yaml"], key=lambda x: x[0])
four = sorted([t for t in grouped_keys if t[1] == "noise_two_per_box.yaml"], key=lambda x: x[0])

total = []
for i in range(3):
    total.append(one[i])
    total.append(two[i])
    total.append(three[i])
    total.append(four[i])

ncols = 4
nrows = int(np.ceil(grouped.ngroups / ncols))

fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(36, 12))

for (key, ax) in zip(total, axes.flatten()):
    g = grouped.get_group(key) \
        .reset_index()
    g["index"] = np.arange(1, len(g) + 1)

    max = 5 if key[1] == "one_per_box.yaml" else 3

    ax.axline((0,max), (1,max), color='red', linestyle='--', label='Max Cumulative Reward')
    ax.set_yscale('symlog')

    print(max)

    g.plot.scatter(x='index',
                   y='mean_reward',
                   ax=ax,
                   title=" ".join(key),
                   xlabel="",
                   ylabel="")

fig.tight_layout()
