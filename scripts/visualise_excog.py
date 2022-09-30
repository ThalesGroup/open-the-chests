import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

results = pd.read_csv("/home/S3G-LABS/u1226/dev/openchests/excog_results/0/results.csv")

results["mean_reward"] = results["mean_reward"].replace(["cant converge"], [None])
results["mean_reward"] = pd.to_numeric(results["mean_reward"], errors='coerce')

agg = results.groupby(["method", "data1"]).agg(
    {"mean_reward": ["max", "mean", "std"],
     "best_trial_per_step_steps": ["min", "mean", "std"]})

best_mean_reward = results.loc[
    results.groupby(["method", "data1"])['mean_reward'].idxmax().reset_index()["mean_reward"]]
best_num_steps = results.loc[
    results.groupby(["method", "data1"])['best_trial_per_step_steps'].idxmin().reset_index()[
        "best_trial_per_step_steps"]]

grouped = results[["method", "data1", "mean_reward"]].groupby(["method", "data1"])

grouped_keys = list(grouped.groups.keys())

one = sorted([t for t in grouped_keys if t[1] == "one_per_box.yaml"], key=lambda x: x[0])
two = sorted([t for t in grouped_keys if t[1] == "one_distinct_per_box.yaml"], key=lambda x: x[0])
three = sorted([t for t in grouped_keys if t[1] == "multiple_per_box.yaml"], key=lambda x: x[0])
four = sorted([t for t in grouped_keys if t[1] == "noise_two_per_box.yaml"], key=lambda x: x[0])

total = []
for i in range(4):
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

    g.plot.scatter(x='index',
                   y='mean_reward',
                   ax=ax,
                   title=" ".join(key),
                   xlabel="",
                   ylabel="")

fig.tight_layout()

