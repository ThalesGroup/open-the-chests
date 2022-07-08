from copy import deepcopy


class Event:
    def __init__(self,
                 e_type: str,
                 e_attributes: dict,
                 t_start: float,
                 t_end: float):
        """
        # TODO
        :param e_type:
        :param e_attributes:
        :param t_start:
        :param t_end:
        """
        self.symbol = {"e_type": e_type, "attr": e_attributes}
        self.start = t_start
        self.end = t_end
        self.duration = t_end - t_start

    def shift(self, delta):
        new = deepcopy(self)
        new.start += delta
        new.end += delta
        return new

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
