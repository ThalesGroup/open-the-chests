import math


class Event:
    """
    Defines an event with a type, attributes, start time, and end time.

    Attributes
    ----------
    type : str
        Identifier for the event (often a single character).
    attributes : dict
        Dictionary of named attributes (e.g., {'color': 'blue'}).
    start : float
        Start time of the event.
    end : float
        End time of the event.
    duration : float
        Duration of the event (end - start).

    Methods
    -------
    get_type() -> str
        Returns the type of the event.
    get_attribute_val(attr: str) -> any
        Returns the value of a specified attribute.
    set_time(t_start: float, t_end: float) -> None
        Sets the start and end times of the event.
    shifted(delta: float) -> Event
        Returns a new event with times shifted by the given delta.
    to_dict() -> dict
        Returns a dictionary representation of the event.
    """

    def __init__(self,
                 e_type: str,
                 e_attributes: dict,
                 t_start: float,
                 t_end: float) -> object:
        """
        Initializes an event with type, attributes, and timing.

        Parameters
        ----------
        e_type : str
            Event type identifier.
        e_attributes : dict
            Dictionary of event attributes.
        t_start : float
            Start time of the event.
        t_end : float
            End time of the event.

        Raises
        ------
        AssertionError
            If t_end < t_start.
        """
        self.duration = None
        self.end = None
        self.start = None
        self.type = e_type
        self.attributes = e_attributes
        self.set_time(t_start, t_end)

    def get_type(self) -> str:
        """Returns the type of the event."""
        return self.type

    def get_attribute_val(self, attr: str):
        """Returns the value for a given attribute key."""
        return self.attributes[attr]

    def get_duration(self):
        """Returns the duration of an event."""
        return self.duration

    def set_time(self, t_start: float, t_end: float) -> None:
        """Sets event start and end times, ensuring correct order."""
        assert t_start <= t_end, "Event start must be ≤ end."
        self.start = t_start
        self.end = t_end
        self.duration = t_end - t_start

    def shifted(self, delta: float) -> "Event":
        """
        Returns a new event shifted in time by a given delta.

        Parameters
        ----------
        delta : float
            Time shift to apply (must not result in negative start time).

        Returns
        -------
        Event
            A new shifted Event instance.
        """
        assert self.start + delta >= 0, (
            f"Shift would result in negative start time: {self.start + delta}"
        )

        # A shifted event differs only in its start/end times; its type and
        # attributes are unchanged, so construct the shifted copy directly. A
        # deep copy here recursively cloned the attributes dict on every sampled
        # event and dominated event-generation time under repeated sampling.
        return Event(self.type, dict(self.attributes),
                     self.start + delta, self.end + delta)

    def to_dict(self) -> dict:
        """Returns dictionary representation of the event."""
        return {"e_type": self.type} | self.attributes | {
            "start": self.start,
            "end": self.end,
            "duration": self.duration
        }

    def __lt__(self, other: "Event") -> bool:
        """Returns True if this event ends before the other."""
        return self.end < other.end

    def __le__(self, other: "Event") -> bool:
        """Returns True if this event ends before or at the same time as the other."""
        return self.end <= other.end

    def __gt__(self, other: "Event") -> bool:
        """Returns True if this event ends after the other."""
        return self.end > other.end

    def __ge__(self, other: "Event") -> bool:
        """Returns True if this event ends after or at the same time as the other."""
        return self.end >= other.end

    def __eq__(self, other: object) -> bool:
        """
        Compares two events for equality.

        Parameters
        ----------
        other : object
            Another Event instance.

        Returns
        -------
        bool
            True if type, attributes, start, and end match.
        """
        if not isinstance(other, Event):
            return NotImplemented
        return (
            self.type == other.type and
            self.attributes == other.attributes and
            math.isclose(self.start, other.start) and
            math.isclose(self.end, other.end)
        )

    def __str__(self) -> str:
        """Returns user-friendly string representation of the event."""
        return f"Event(type='{self.type}', attr={self.attributes}, start={round(self.start, 3)}, end={round(self.end, 3)})"

    def __repr__(self) -> str:
        """Returns debug string representation of the event."""
        return str(self)
