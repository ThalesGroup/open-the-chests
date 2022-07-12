from Elements.Event import Event
import random

import plotly.express as px
import pandas as pd

import plotly.figure_factory as ff
import plotly.express as px

all_event_types = ["A", "B", "C"]
all_event_attributes = {"fg": ["red", "blue", "green"], "bg": ["red", "blue", "green"]}


# TODO replace with truncated normal
def instantiate(e_type: str = None, attributes: dict = {}, duration_dist: (int, int) = (2, 1)):
    if e_type is None:
        e_type = random.choice(all_event_types)
    for attr, attr_values in all_event_attributes.items():
        if attr not in attributes:
            attributes[attr] = random.choice(attr_values)
    duration_inst = random.normalvariate(*duration_dist)
    return Event(e_type, attributes, 0, duration_inst)


# TODO is deepcopy really needed?
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


"""
$a1 : A(bg == 'blue', fg == 'yellow'),
$c1 : C(bg  == 'red', fg == 'red', this after $a1),
$c2 : C(bg == 'green', fg == 'yellow', this during $c1),
$a2 : A(bg == 'blue', fg == 'yellow', this != $a1, this metby $c1)

"""


def test():
    event_list = []
    a1 = instantiate("A", {"bg": "blue"}, (4, 2))  # let fg be random duration normal mean 4 var 2
    event_list.append(a1)

    c1 = instantiate("C", {"fg": "red"}, (10, 1))  # let bg be random
    c1 = after(c1, a1, (2, 1))  # c1 after a1 with gap in-between of mean 1 var 1
    event_list.append(c1)

    c2 = instantiate("C", {}, (4, 1))  # all is random
    c2 = during(c2, c1)  # c2 is during c1
    event_list.append(c2)

    a2 = instantiate("A")  # all random default duration mean 1 var 1
    a2 = met_by(a2, c1)  # a2 is met by c1
    event_list.append(a2)

    return event_list


instructions = [{"command": "instantiate", "parameters": ("A", {"bg": "blue"}, (4, 2)), "variable_name": "a1"},
                {"command": "instantiate", "parameters": ("C", {"fg": "red"}, (10, 1)), "variable_name": "c1"},
                {"command": "after", "parameters": ("c1", "a1"), "variable_name": "c1", "gap_dist": (2, 1)},
                {"command": "instantiate", "parameters": ("C", {}, (4, 1)), "variable_name": "c2"},
                {"command": "during", "parameters": ("c2", "c1"), "variable_name": "c2"},
                {"command": "instantiate", "parameters": ("A",), "variable_name": "a2"},
                {"command": "met_by", "parameters": ("a2", "c1"), "variable_name": "c1"}]

allen_functions = {"after": after, "during": during, "met_by": met_by}


def generate_pattern(instructions):
    event_list = []
    variables = dict()
    for instr in instructions:
        if instr["command"] == "instantiate":
            event = instantiate(*instr["parameters"])
            variables[instr["variable_name"]] = event
            if not event_list:
                event_list.append(event)
        else:
            params = (variables[param] for param in instr["parameters"])
            if instr["command"] == "after":
                event = allen_functions[instr["command"]](*params, instr["gap_dist"])
            else:
                event = allen_functions[instr["command"]](*params)
            variables[instr["variable_name"]] = event
            event_list.append(event)
    return event_list


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

        list_df.append(dict(Resource=str(event.symbol["e_type"]),
                            Start=event.start,
                            Finish=event.end,
                            Color=event.symbol["attr"]["bg"],
                            Task=str(line_index)))

    df = pd.DataFrame(list_df)

    print(df)

    """
    fig = px.timeline(df, x_start="Start", x_end="Finish", y="Resource")
    fig.update_yaxes(autorange="reversed")  # otherwise tasks are listed from the bottom up
    fig.update_xaxes(tickformat="%H:%M:%S")
    fig.show()
    """

    fig = ff.create_gantt(df, index_col='Resource', group_tasks=True)
    fig.update_layout(xaxis_type='linear')
    fig.update_yaxes(autorange="reversed")  # otherwise, tasks are listed from the bottom up


"""
def after(e1: (bool, Event), e2: (bool, Event)):
    if e1[0]:
        e1_end = e1[1].end
    else:
        e1_end = e1[1][-1].end

    if e2[0]:
        e2[1].start += e1_end
        e2[1].end += e1_end
        return False, [e1, e2]
    else:
        for e in e2[1]:
            e += e1_end
            if e1[0]:
                return False, [e1] + e2[1]
            else:
                return False, e1[1] + e2[1]


print(after(after((True, Event("A", [0], 0, 5)), (True, Event("A", [0], 0, 5))),
            after((True, Event("A", [0], 0, 5)), (True, Event("A", [0], 0, 5)))))
"""
