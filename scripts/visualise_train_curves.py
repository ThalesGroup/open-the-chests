from matplotlib import pyplot as plt

from openthechests.src.utils.modified_plotting import X_TIMESTEPS, plot_results

models = ["A2C", "DQN", "PPO", "TRPO"]
confs = ["one_per_box", "one_distinct_per_box", "multiple_per_box", "noise_two_per_box"]
ncols = len(models)
nrows = len(confs)


fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(36, 12))
combos = []

for model in models:
    for config in confs:
        combos.append((model, config))

for (key, ax) in zip(combos, axes.flatten()):
    model, config = key

    max = 5 if (config == "one_per_box" or config == "noise_two_per_box") else 3

    ax.axline((0, max), (1, max), color='red', linestyle='--', label='Max Cumulative Reward')

    plot_results([f"./delay_variation0/{model}/{config}/"], 1e5, X_TIMESTEPS,
                                     f"{model}  : ({config})", ax=ax)

fig.tight_layout()
