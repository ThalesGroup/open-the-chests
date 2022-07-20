import random

import numpy as np

from Elements.Event import Event


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


def addAnnot(df, fig):
    for i in df:
        x_pos = (i['Finish'] - i['Start']) / 2 + i['Start']
        for j in fig['data']:
            print("-------------------------")
            print(i)
            print("-------------------------")
            print(j)
            print("-------------------------")
            if j['name'] == i['Label']:
                y_pos = (j['y'][0] + j['y'][1] + j['y'][2] + j['y'][3]) / 4
        fig['layout']['annotations'] += tuple([dict(x=x_pos, y=y_pos, text=i['Label'], font={'color': 'black'})])


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
            if key in ["open", "active"]:
                final_dict[key] = np.array([int(xi) for xi in final_dict[key]])
    return final_dict


def numerise_types_and_attributes(all_event_types, all_event_attributes):
    all_event_types = [i for i in range(len(all_event_types))]
    for key, val in all_event_attributes.items():
        all_event_attributes[key] = [i for i in range(len(all_event_attributes[key]))]
    return all_event_types, all_event_attributes


allen_functions = {"after": after, "during": during, "met_by": met_by}
