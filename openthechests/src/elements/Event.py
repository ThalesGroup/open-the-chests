import math
from copy import deepcopy


class Event:
    """
    Define an event object with a type, attributes, a beginning, and an end.

    Attributes:
    -----------
    type : str
        The type describing the event, usually a single character for simpler environments.
    attributes : dict
        A dictionary of attributes for the event, following the form {'attribute_name': 'attribute value'}.
    start : float
        The start time of the event.
    end : float
        The end time of the event.
    duration : float
        The duration of the event, calculated as t_end - t_start.

    Methods:
    --------
    get_type():
        Returns the type of the event.
    get_attribute_val(attr):
        Returns the value of a specified attribute.
    set_time(t_start, t_end):
        Sets the start and end times of the event, ensuring that t_end >= t_start.
    shifted(delta):
        Shifts the event's start and end times by a fixed value.
    to_dict():
        Returns a dictionary representation of the event.

    Hidden Methods:
    --------
    __lt__(other):
        Compares the end times of two events to determine if this event ends before the other.
    __le__(other):
        Compares the end times of two events to determine if this event ends before or at the same time as the other.
    __gt__(other):
        Compares the end times of two events to determine if this event ends after the other.
    __ge__(other):
        Compares the end times of two events to determine if this event ends after or at the same time as the other.
    __eq__(other):
        Checks if two events are equal by comparing their type, attributes, start time, and end time.
    __str__():
        Returns a string representation of the event.
    __repr__():
        Returns a string representation of the event for debugging purposes.
    """
    def __init__(self,
                 e_type: str,
                 e_attributes: dict,
                 t_start: float,
                 t_end: float) -> object:
        """
        Initializes an event object with a type, attributes, a beginning, and an end.

        :param e_type: str
            The type describing the event using a string, usually just one character suffices for simpler environments.
        :param e_attributes: dict
            A dictionary of attributes following the form {'attribute_name': 'attribute value'}.
        :param t_start: float
            The start time of the event.
        :param t_end: float
            The end time of the event.

        Note: Event end time should be superior to event beginning: t_end >= t_start
        """
        self.duration = None
        self.end = None
        self.start = None
        self.type = e_type
        self.attributes = e_attributes
        self.set_time(t_start, t_end)

    def get_type(self):
        return self.type

    def get_attribute_val(self, attr):
        return self.attributes[attr]

    def set_time(self, t_start, t_end):
        assert t_start <= t_end, "Event beginning must be inferior to event end."
        self.start = t_start
        self.end = t_end
        self.duration = t_end - t_start

    def shifted(self, delta):
        """
        Shifts the event's start and end times by a fixed value.

        :param delta: float
            The value by which to shift the event.
        :return: Event
            A copy of the event with new start and end times.
        """
        assert self.start + delta >= 0, f"Cannot start event sooner than 0, shifting by {delta} would lead to " \
                                        f"starting at {self.start + delta} "

        new = deepcopy(self)
        new.start += delta
        new.end += delta
        return new

    def to_dict(self):
        return {"e_type": self.type} | \
               self.attributes | \
               {"start": self.start, "end": self.end, "duration": self.duration}

    def __lt__(self, other):
        return self.end < other.end

    def __le__(self, other):
        return self.end <= other.endpass

    def __gt__(self, other):
        return self.end > other.end

    def __ge__(self, other):
        return self.end >= other.end

    def __str__(self):
        return f"Event('e_type': {self.type}, " \
               f"'attr': {self.attributes}, " \
               f"'start' : {self.start}, 'end': {self.end})"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        """
        Checks if two events are equal by comparing their type, attributes, start time, and end time.

        :param other: Event
            The other event to compare against.
        :return: bool
            True if events are equal, False otherwise.
        """
        if not isinstance(other, Event):
            return NotImplemented
        return (self.type == other.type and
                self.attributes == other.attributes and
                math.isclose(self.start, other.start) and
                math.isclose(self.end, other.end))

