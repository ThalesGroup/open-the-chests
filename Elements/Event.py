import math
from copy import deepcopy


# TODO doc (priority 4)

class Event:
    def __init__(self,
                 e_type: str,
                 e_attributes: dict,
                 t_start: float,
                 t_end: float):
        # TODO (priority 2) reorganise event object structure all the dictionaries are awkward
        """
        :param e_type:
        :param e_attributes:
        :param t_start:
        :param t_end:
        """
        self.symbol = {"e_type": e_type, "attr": e_attributes}
        self.start = t_start
        self.end = t_end
        self.duration = t_end - t_start if (t_end != math.inf) else math.inf

    def set_time(self, t_start, t_end):
        self.start = t_start
        self.end = t_end
        self.duration = t_end - t_start

    def shift(self, delta):
        """

        :param delta:
        :return:
        """
        new = deepcopy(self)
        new.start += delta
        new.end += delta
        return new

    def to_dict(self):
        return {"e_type": self.symbol["e_type"]} | \
               self.symbol["attr"] | \
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
        return str(self.symbol) + " : " + str(self.start) + " -> " + str(self.end)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.symbol == other.symbol and abs(self.duration - other.duration) <= min(self.duration, other.duration)
