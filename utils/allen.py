import random

from Elements.Event import Event
from utils.utils import my_normal


def after(second: Event, first: Event, gap_dist: (int, int)):
    gap_duration = my_normal(**gap_dist)
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


allen_functions = {"after": after, "during": during, "met_by": met_by}