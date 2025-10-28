# TODO Priority 1: review and refactor script files and add more allen functions
from copy import deepcopy
from typing import List, Dict

import numpy as np

from openthechests.openthechests.src.elements import Event
from openthechests.openthechests.src.utils.helper_functions import my_normal


def overlapped(second: Event, first: Event):
    """
    Allows to define the allen relation "overlaps" between two events.
    The second event is set to begin at a randomly chosen time overlapping with the first one.

    :param second: The second event to be placed after the first one.
    :param first: The first event serving as reference to the second one.
    :return: The transformed second event
    """
    overlap_size = min(first.duration, second.duration)
    overlap_size = np.random.uniform(0, overlap_size)
    new_event = second.shifted(first.end - overlap_size)
    return new_event


def after(second: Event, first: Event, gap_dist: (int, int)):
    """
    Allows to define the allen relation "after" between two events.
    The second event is placed after the first one, while respecting a certain gap distance.

    :param second: The second event to be placed after the first one.
    :param first: The first event serving as reference to the second one.
    :param gap_dist: The gap to respect, defined using (mu, sigma) and sampled via a gaussian.
    :return: The transformed second event
    """
    gap_duration = my_normal(**gap_dist)
    second_start = first.end + gap_duration
    new_event = second.shifted(second_start)
    return new_event


def during(second: Event, first: Event):
    """
    Allows to define the allen relation "during" between two events.
    The second event is placed during the first one,
    where the lag between the beginning o the two events is generated using a uniform distribution.

    :param second: the second event to be placed during the first one.
    :param first: The first event to be used as reference.
    :return: The transformed second event
    """
    assert (first.duration >= second.duration), \
        f"An event can be longer than the one containing it! {first.duration} > {second.duration}"
    gap_size = np.random.uniform(0, first.duration - second.duration)
    second_start = first.start + gap_size
    new_event = second.shifted(second_start)
    return new_event


def met_by(second: Event, first: Event):
    """
    Allows to define the allen relation "met by" between two events.
    The second event is placed immediately after the end of the first one.

    :param second: The second event to be placed right after the first one.
    :param first: The first event serving as reference to the second one.
    :return: The transformed second event
    """
    return second.shifted(first.end)


def starts(second: Event, first: Event):
    """
    Allows to define the allen relation "starts" between two events.
    The second event is placed to start the first one and end before the first starts.

    :param second: The second event to be placed at the start of the first one.
    :param first: The first event serving as reference to the second one.
    :return: The transformed second event
    """

    assert (first.duration >= second.duration), \
        f"An event can be longer than the one containing it! {first.duration} > {second.duration}"

    return second.shifted(first.start)


def ends(second: Event, first: Event):
    """
    Allows to define the allen relation "ends" between two events.
    The second event is placed to end the first one and start after the first finishes.

    :param second: The second event to be placed at the start of the first one.
    :param first: The first event serving as reference to the second one.
    :return: The transformed second event
    """

    assert (first.duration >= second.duration), \
        f"An event can be longer than the one containing it! {first.duration} > {second.duration}"

    end_diff = first.end - second.end
    return second.shifted(end_diff)


def equals(second: Event, first: Event):
    """
    Allows to define the allen relation "equals" between two events.
    The second event is placed to have the same start and end times as the first one.
    Attention this will overwrite the original time of the event.

    :param second: The second event to be placed at the same time as the first one.
    :param first: The first event serving as reference to the second one.
    :return: The transformed second event
    """

    new_event = deepcopy(second)
    new_event.start = first.start
    new_event.end = first.end
    return new_event


allen_functions = {"after": after,
                   "during": during,
                   "met_by": met_by,
                   "overlapped": overlapped,
                   "starts": starts,
                   "ends": ends,
                   "equals": equals}

allen_relations = allen_functions.keys()
