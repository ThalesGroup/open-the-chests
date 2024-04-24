import math
from copy import deepcopy


class Event:
    def __init__(self,
                 e_type: str,
                 e_attributes: dict,
                 t_start: float,
                 t_end: float):
        """
        Define an event object with a type, attributes, a beginning and an end.

        :param e_type: type describing event using string, usually just one character suffices for simpler environments
        :param e_attributes: dictionary of attributes following the form {'attribute_name': 'attribute value'}
        :param t_start: _time of start of event
        :param t_end: _time of end of event

        Note: Event end _time should be superior to event beginning : t_end >= t_start
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
        Shift event start and end by a fixed value.

        :param delta: Value by which to shift the event.
        :return: Copy of event with new start and end times
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

