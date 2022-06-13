class Event:
    def __init__(self,
                 e_type: str,
                 e_attributes: list,
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

    def __str__(self):
        return str(self.symbol) + " : " + str(self.start) + " -> " + str(self.end)

    def __repr__(self):
        return str(self)
