from typing import Callable, List, Optional, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import List, Union

from stable_baselines3.common.monitor import load_results

X_TIMESTEPS = "timesteps"
X_EPISODES = "episodes"
X_WALLTIME = "walltime_hrs"
POSSIBLE_X_AXES = [X_TIMESTEPS, X_EPISODES, X_WALLTIME]
EPISODES_WINDOW = 100


def rolling_window(array: np.ndarray, window: int) -> np.ndarray:
    """
    Apply a rolling window to a np.ndarray
    :param array: the input Array
    :param window: length of the rolling window
    :return: rolling window on the input array
    """
    shape = array.shape[:-1] + (array.shape[-1] - window + 1, window)
    strides = array.strides + (array.strides[-1],)
    return np.lib.stride_tricks.as_strided(array, shape=shape, strides=strides)


def window_func(var_1: np.ndarray, var_2: np.ndarray, window: int, func: Callable) -> Tuple[np.ndarray, np.ndarray]:
    """
    Apply a function to the rolling window of 2 arrays
    :param var_1: variable 1
    :param var_2: variable 2
    :param window: length of the rolling window
    :param func: function to apply on the rolling window on variable 2 (such as np.mean)
    :return:  the rolling output with applied function
    """
    var_2_window = rolling_window(var_2, window)
    function_on_var2 = func(var_2_window, axis=-1)
    return var_1[window - 1:], function_on_var2


def ts2xy(data_frame: pd.DataFrame, x_axis: str) -> Tuple[np.ndarray, np.ndarray]:
    """
    Decompose a data frame variable to x ans ys
    :param data_frame: the input data
    :param x_axis: the axis for the x and y output
        (can be X_TIMESTEPS='timesteps', X_EPISODES='episodes' or X_WALLTIME='walltime_hrs')
    :return: the x and y output
    """
    if x_axis == X_TIMESTEPS:
        x_var = np.cumsum(data_frame.l.values)
        y_var = data_frame.r.values
    elif x_axis == X_EPISODES:
        x_var = np.arange(len(data_frame))
        y_var = data_frame.r.values
    elif x_axis == X_WALLTIME:
        # Convert to hours
        x_var = data_frame.t.values / 3600.0
        y_var = data_frame.r.values
    else:
        raise NotImplementedError
    return x_var, y_var


def plot_curves(
        xy_list: List[Tuple[np.ndarray, np.ndarray]], x_axis: str, title: str, figsize: Tuple[int, int] = (8, 2),
        ax=None,
) -> None:
    """
    plot the curves
    :param xy_list: the x and y coordinates to plot
    :param x_axis: the axis for the x and y output
        (can be X_TIMESTEPS='timesteps', X_EPISODES='episodes' or X_WALLTIME='walltime_hrs')
    :param title: the title of the plot
    :param figsize: Size of the figure (width, height)
    """

    # plt.figure(title, figsize=figsize)
    max_x = max(xy[0][-1] for xy in xy_list)
    min_x = 0
    for (_, (x, y)) in enumerate(xy_list):
        ax.scatter(x, y, s=2)
        # Do not plot the smoothed curve at all if the timeseries is shorter than window size.
        if x.shape[0] >= EPISODES_WINDOW:
            # Compute and plot rolling mean with window of size EPISODE_WINDOW
            x, y_mean = window_func(x, y, EPISODES_WINDOW, np.mean)
            ax.plot(x, y_mean)
    ax.axis(xmin=min_x, xmax=max_x)
    ax.title.set_text(title)
    ax.set_xlabel(x_axis)
    ax.set_ylabel("Episode Rewards")
    # ax.tight_layout()


def plot_results(
        dirs: List[str], num_timesteps: Optional[int], x_axis: str, task_name: str, figsize: Tuple[int, int] = (8, 2),
        ax=None,
) -> None:
    """
    Plot the results using csv files from ``Monitor`` wrapper.
    :param dirs: the save location of the results to plot
    :param num_timesteps: only plot the points below this value
    :param x_axis: the axis for the x and y output
        (can be X_TIMESTEPS='timesteps', X_EPISODES='episodes' or X_WALLTIME='walltime_hrs')
    :param task_name: the title of the task to plot
    :param figsize: Size of the figure (width, height)
    """

    data_frames = []
    for folder in dirs:
        data_frame = load_results(folder)
        if num_timesteps is not None:
            data_frame = data_frame[data_frame.l.cumsum() <= num_timesteps]
        data_frames.append(data_frame)
    xy_list = [ts2xy(data_frame, x_axis) for data_frame in data_frames]
    plot_curves(xy_list, x_axis, task_name, figsize, ax=ax)


def draw_event_sequence_matplot(events: List[Union[dict, "Event"]],
                                start_time: float = 0,
                                end_time: float = 50,
                                env_name: str = "Example") -> None:
    """
    Draw a horizontal timeline of events using matplotlib.

    Each event is shown as a colored bar, with its label centered inside.
    Events are placed on separate rows if they overlap in time.

    Parameters
    ----------
    events : list of dict or list of Event
        Sequence of events to display. Each event must provide:
        - start_time (float) or .start (for Event)
        - end_time (float) or .end (for Event)
        - symbol (str) or .type (for Event)
        - bg_color (str) or attributes["bg"] (for Event)
        - symbol_color (str) or attributes["fg"] (for Event)
    start_time : float, optional
        Minimum time to display on the x-axis.
    end_time : float, optional
        Maximum time to display on the x-axis.
    env_name : str, optional
        Name of the environment to show in the plot title.

    Returns
    -------
    None
        Displays a matplotlib figure of the event timeline.
    """
    fig, ax = plt.subplots(figsize=(15, 5))  # wide figure for better readability

    last_event_end_times = []  # Tracks last end time per row to avoid overlap
    height = 1  # Height of each event bar

    for event in events:
        # Support both dicts and Event objects
        if hasattr(event, "start"):  # Event instance
            event_name = getattr(event, "type", "?")
            start = event.start
            end = event.end
            color = event.attributes.get("bg", "#CCCCCC")
            text_color = event.attributes.get("fg", "#000000")
        else:  # dict format
            event_name = event.get("symbol", "?")
            start = event.get("start_time", 0)
            end = event.get("end_time", 0)
            color = event.get("bg_color", "#CCCCCC")
            text_color = event.get("symbol_color", "#000000")

        # Determine row placement (to avoid overlaps)
        line = 0
        while line < len(last_event_end_times):
            if start >= last_event_end_times[line]:  # Fits in this row
                break
            line += 1
        if line == len(last_event_end_times):
            last_event_end_times.append(end)
        else:
            last_event_end_times[line] = end

        # Draw rectangle for event
        y_pos = line * (height + 0.5)
        rect_width = max(end - start, 0.1)  # Ensure non-zero width
        rect = patches.Rectangle((start, y_pos), rect_width, height,
                                 color=color, alpha=0.7)
        ax.add_patch(rect)

        # Add centered label
        ax.text(start + rect_width / 2, y_pos + height / 2,
                event_name, ha='center', va='center',
                color=text_color, fontsize=12, fontweight='bold')

    # Configure plot
    ax.set_xlim(start_time, end_time)
    ax.set_ylim(0, len(last_event_end_times) * (height + 0.5))
    ax.set_xlabel("Time")
    ax.set_ylabel("Event Sequences")
    ax.set_title(f"Observed Event Timeline ({env_name})")
    plt.show()
