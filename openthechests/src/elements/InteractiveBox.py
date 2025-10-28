class InteractiveBox:
    """
    A class representing an openable, stateful interactive box used in a temporal activity environment.

    Each box can go through several internal states:
    - `_open`: the box has been opened successfully.
    - `_ready`: the box is ready to be opened by a valid press.
    - `active`: the box is actively responding to the environment.

    These boxes typically respond to event-based signals and evolve according to internal rules
    defined in the environment engine.

    Attributes
    ----------
    id : int
        Unique identifier for the box.
    verbose : bool
        If True, print debug messages during transitions.
    state : dict
        Current state of the box with boolean flags: {'_open', '_ready', 'active'}.
    num_deactivations : int
        Counter tracking how many times the box was deactivated.

    Methods
    -------
    get_state() -> dict
        Returns the current internal state dictionary.
    is_ready() -> bool
        Checks whether the box is in the `_ready` state.
    is_open() -> bool
        Checks whether the box is `_open`.
    is_active() -> bool
        Checks whether the box is currently active.
    reset() -> None
        Resets the box state to initial conditions.
    press_button() -> bool
        Simulates a button press and attempts to open the box.
    update(signal: list = None) -> None
        Applies signal-driven updates according to internal rules.

    Private Methods
    ---------------
    _open() -> None
        Internally sets the box to `_open`, and deactivates it.
    _activate() -> None
        Marks the box as active (initializes interaction).
    _deactivate() -> None
        Deactivates the box, clearing all other states.
    _ready() -> None
        Marks the box as `_ready`, signaling it can be opened.
    """

    def __init__(self, id: int, verbose: bool = True):
        """
        Initialize a new InteractiveBox instance.

        Parameters
        ----------
        id : int
            The unique identifier for the box.
        verbose : bool, optional
            If True, enables debug messages (default: True).
        """
        self.id = id
        self.verbose = verbose
        self.state = {"_open": False, "_ready": False, "active": False}
        self.num_deactivations = 0

    def get_state(self) -> dict:
        """Return the current state of the box."""
        return self.state

    def is_ready(self) -> bool:
        """Return True if the box is in the `_ready` state."""
        return self.state["_ready"]

    def is_open(self) -> bool:
        """Return True if the box is `_open`."""
        return self.state["_open"]

    def is_active(self) -> bool:
        """Return True if the box is currently active."""
        return self.state["active"]

    def reset(self) -> None:
        """
        Reset the box to its initial state (inactive, not ready, not open).
        """
        self.state = {"_open": False, "_ready": False, "active": False}
        self.num_deactivations = 0

    def _open(self) -> None:
        """
        Open the box (if active and ready), and then deactivate it.

        Raises
        ------
        AssertionError
            If the box is not active or not ready.
        """
        assert self.state["active"], "Cannot _open a deactivated box."
        assert self.state["_ready"], "Cannot _open a box unless it's _ready."

        if self.verbose:
            print(f"Opening box {self.id}.")
        self.state["_open"] = True
        self.state["_ready"] = False
        self.state["active"] = False

    def _activate(self) -> None:
        """
        Activate the box, enabling it to begin interaction.

        Raises
        ------
        AssertionError
            If the box is already active, ready, or open.
        """
        assert not self.state["_open"], "Cannot _activate an already opened box."
        assert not self.state["_ready"], "Box shouldn't be _ready on activation."
        assert not self.state["active"], "Box is already active."

        if self.verbose:
            print(f"Activating box {self.id}.")
        self.state["active"] = True
        self.state["_ready"] = False
        self.state["_open"] = False

    def _deactivate(self) -> None:
        """
        Deactivate the box and reset its interaction state.

        Raises
        ------
        AssertionError
            If the box is already opened or not active.
        """
        assert not self.state["_open"], "Cannot _deactivate an opened box."
        assert self.state["active"], "Box must be active to be deactivated."

        if self.verbose:
            print(f"Deactivating box {self.id}.")
        self.num_deactivations += 1
        self.state["active"] = False
        self.state["_ready"] = False
        self.state["_open"] = False

    def _ready(self) -> None:
        """
        Mark the box as ready to be opened.

        Raises
        ------
        AssertionError
            If the box is not active.
        """
        assert self.state["active"], "Deactivated box cannot be marked _ready."

        if self.verbose:
            print(f"Ready box {self.id}.")
        self.state["active"] = True
        self.state["_ready"] = True
        self.state["_open"] = False

    def press_button(self) -> bool:
        """
        Simulates a button press on the box.

        Returns
        -------
        bool
            True if the box was successfully opened, False otherwise.
        """
        if not self.state["_open"]:
            if self.state["active"] and self.state["_ready"]:
                self._open()
                return True
            else:
                if self.verbose:
                    print(f"Unsuccessful opening of box {self.id}.")
        return False

    def update(self, signal: list = None) -> None:
        """
        Update the box state based on environment signals.

        This method is called once per environment step to evolve the box's internal state.
        It handles timeouts (deactivating if a press opportunity is missed), reactivation
        (if the delay has passed), and readiness (if the pattern is currently satisfied).

        Parameters
        ----------
        signal : list of str, optional
            A list of state transition signals used to guide the update process.
            Possible signal values include:

            - "active"     : Triggers reactivation of the box (e.g., after cooldown).
            - "satisfied"  : Indicates that the box's pattern condition has been satisfied,
                             and it can now become `_ready`.

            Multiple signals may be passed together in one update call, e.g.:
                box.update(signal=["active", "satisfied"])

            This design allows simultaneous transitions (e.g., reactivation + readiness)
            in a single environment step, enabling efficient and expressive temporal logic.
        """

        if signal is None:
            signal = []

        if not self.state["_open"]:
            if self.state["active"]:
                # Timeout: box was ready but no button press occurred
                if self.state["_ready"]:
                    self._deactivate()
            if not self.state["active"]:
                if "active" in signal:
                    self._activate()
            if "satisfied" in signal:
                self._ready()
