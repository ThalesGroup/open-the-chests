import random

import numpy as np
import pandas as pd

from Elements.Event import Event

import plotly.figure_factory as ff


def after(second: Event, first: Event, gap_dist: (int, int)):
    gap_duration = random.normalvariate(*gap_dist)
    second_start = first.end + gap_duration
    new_event = second.shift(second_start)
    return new_event


def during(second: Event, first: Event):
    assert (first.duration >= second.duration), "An event can be longer than the one containing it!"
    gap_size = random.uniform(0, first.duration - second.duration)
    second_start = first.start + gap_size
    new_event = second.shift(second_start)
    return new_event


def met_by(second: Event, first: Event):
    return second.shift(first.end)


def print_event_list(event_list):
    list_df = []
    line_end_times = [0]
    for event in event_list:
        line_index = 0
        while line_index + 1 <= len(line_end_times) and line_end_times[line_index] >= event.end:
            line_index += 1
        if line_index + 1 <= len(line_end_times):
            line_end_times[line_index] = event.end
        else:
            line_end_times.append(event.end)

        list_df.append(dict(Resource=event.symbol["e_type"],
                            Start=event.start,
                            Finish=event.end,
                            Color=event.symbol["attr"]["bg"],
                            Task=str(line_index)))

    df = pd.DataFrame(list_df)

    fig = ff.create_gantt(df, index_col='Resource', group_tasks=True)
    fig.update_layout(xaxis_type='linear')
    fig.update_yaxes(autorange="reversed")  # otherwise, tasks are listed from the bottom up
    fig.show()


def process_obs(obs: dict):
    final_dict = dict()
    for key, value in obs.items():
        if type(value) == dict:
            final_dict = final_dict | value
        elif type(value) == Event:
            final_dict = final_dict | value.to_dict()
        else:
            final_dict[key] = value

    for key, value in final_dict.items():
        # TODO total workaround must fix
        if key not in ["e_type", "fg", "bg"]:
            final_dict[key] = np.array(value)
            if key in ["start", "end", "duration"]:
                final_dict[key] = final_dict[key].reshape(-1)
    return final_dict


def numerise_types_and_attributes(all_event_types, all_event_attributes):
    all_event_types = [i for i in range(len(all_event_types))]
    for key, val in all_event_attributes.items():
        all_event_attributes[key] = [i for i in range(len(all_event_attributes[key]))]
    return all_event_types, all_event_attributes


allen_functions = {"after": after, "during": during, "met_by": met_by}
