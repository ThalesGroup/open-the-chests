import pickle

import numpy as np
from matplotlib import pyplot as plt

from src.utils.stolen_plotting import plot_results, X_TIMESTEPS

models = ["A2C", "DQN", "PPO", "TRPO"]
confs = ["one_per_box", "one_distinct_per_box", "multiple_per_box", "noise_two_per_box"]
ncols = len(models)
nrows = len(confs)


fig, axes = plt.subplots(nrows=1, ncols=4, figsize=(4, 1))
print(axes)
combos = []

ax = 0
for config in confs:
    vals, names, xs = [],[],[]
    j = 0
    for model in models:
        j+=1
        data = []
        with open(f"./delay_variation3/{model}/{config}/outfile", 'rb') as fp:
            for i in range(5):
                itemlist = pickle.load(fp)
                data.append(itemlist)
            xs.append(np.random.normal(j, 0.04, len(data[2])))
            vals.append(data[2])
            names.append(model)

    # print(vals)
    # print(xs)
    # print(names)
    axes[ax].boxplot(vals, labels=names)

    max = 5 if (config == "one_per_box" or config == "noise_two_per_box") else 3

    axes[ax].axline((0, max), (1, max), color='red', linestyle='--', label='Max Cumulative Reward')

    palette = ['r', 'g', 'b', 'y']
    for x, val, c in zip(xs, vals, palette):
        axes[ax].scatter(x, val, alpha=0.4, color=c)
    ax+=1


# for (key, ax) in zip(combos, axes.flatten()):
#     model, config = key

    # max = 5 if (config == "one_per_box" or config == "noise_two_per_box") else 3

    # ax.axline((0, max), (1, max), color='red', linestyle='--', label='Max Cumulative Reward')

    # plot_results([f"./delay_variation2/{model}/{config}/"], 1e5, X_TIMESTEPS,
    #                                  f"{model}  : ({config})", ax=ax)



    # plt.boxplot(vals, labels=names)
    # palette = ['r', 'g', 'b', 'y']
    # for x, val, c in zip(xs, vals, palette):
    #     plt.scatter(x, val, alpha=0.4, color=c)


fig.tight_layout()



