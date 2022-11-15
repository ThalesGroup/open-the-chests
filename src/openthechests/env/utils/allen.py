import random

from src.openthechests.env.elements.Event import Event
from src.openthechests.src import my_normal


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
    gap_size = random.uniform(0, first.duration - second.duration)
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


allen_functions = {"after": after, "during": during, "met_by": met_by}