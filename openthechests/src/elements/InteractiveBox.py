
class InteractiveBox:
    """
    An openable box that allows interaction.
    It possesses three state indicators: _open, _ready, and active.
    The box is initialized with a pattern which defines how the box changes states.

    Attributes:
    -----------
    id : int
        The identifier of the box.
    verbose : bool
        A flag to give details during operations.
    state : dict
        A dictionary representing the current state of the box.
    num_deactivations : int
        A counter for the number of times the box has been deactivated.

    Methods:
    --------
    get_state():
        Returns the current state of the box.
    is_ready():
        Checks if the box is in the _ready state.
    is_open():
        Checks if the box is in the _open state.
    is_active():
        Checks if the box is in the active state.
    reset():
        Resets the box to its initial conditions.
    press_button():
        Attempts to open the box via a button press.
    update(signal=None):
        Updates the box status using the current time information.

    Hidden Methods:
    --------
    _open():
        Opens the box, deactivates it, and marks it as not _ready.
    _activate():
        Activates the box, marking it as not _ready and not _open.
    _deactivate():
        Deactivates the box, marking it as not _ready and not _open.
    _ready():
        Makes the box _ready to open, removing its active status.
    """
    def __init__(self,
                 id: int,
                 verbose: bool=True):
        """
        Initializes an InteractiveBox with the given ID and verbosity flag.

        :param id: int
            The identifier of the box.
        :param verbose: bool
            A flag to give details during operations.
        """
        self.id = id
        self.verbose = verbose
        self.state = {"_open": False, "_ready": False, "active": False}
        self.num_deactivations = 0

    def get_state(self):
        return self.state

    def is_ready(self):
        return self.state["_ready"]

    def is_open(self):
        return self.state["_open"]

    def is_active(self):
        return self.state["active"]

    def reset(self):
        """
        Resets the box to its initial conditions, not opened, not _ready, and active,
        and regenerates its event stack starting at a selected time.
        """
        self.state = {"_open": False, "_ready": False, "active": False}
        self.num_deactivations = 0

    def _open(self):
        """
        Opens the box, deactivates it once it is opened, and marks it as not _ready.
        """
        assert self.state["active"], "Cannot _open a deactivated box."
        assert self.state["_ready"], "Cannot _open a box if it isn't _ready first."

        if self.verbose:
            print(f"Opening box {self.id}")
        self.state["_open"] = True
        self.state["_ready"] = False
        self.state["active"] = False

    def _activate(self):
        """
        Activates the box, marking it as not _ready and not _open.
        """
        assert not self.state["_open"], "Cannot _activate an opened box."
        assert not self.state["_ready"], "Newly activated boxes shouldn't be _ready."
        assert not self.state["active"], "Trying to _activate a box that is already active."

        if self.verbose:
            print(f"Activating box {self.id}")

        self.state["active"] = True
        self.state["_ready"] = False
        self.state["_open"] = False

    def _deactivate(self):
        """
        Deactivates box, marking it as not _ready and not _open
        """

        assert not self.state["_open"], "Cannot _deactivate an opened box."
        assert self.state["active"], "A box must first be active to _deactivate it.."

        if self.verbose:
            print(f"Deactivating box {self.id}")

        self.num_deactivations += 1
        self.state["active"] = False
        self.state["_ready"] = False
        self.state["_open"] = False

    def _ready(self):
        """
        Makes box _ready to _open, removing its active status
        """
        assert self.state["active"], "Deactivated box cannot be _ready."

        if self.verbose:
            print(f"Ready box {self.id}")

        self.state["active"] = True
        self.state["_ready"] = True
        self.state["_open"] = False

    def press_button(self):
        """
        Attempts to open the box via a button press.
        If the box is active and ready, it will open.

        :return: bool
            True if the box is successfully opened, False otherwise.
        """
        if not self.state["_open"]:  # if the box has not been opened already
            if self.state["active"] and self.state["_ready"]:  # if the box is active and _ready to _open
                self._open()
                return True
        return False  # in all other cases return false

    def update(self, signal=None):
        """
        Updates the box status using the current time information.
        During each environment step, each box is updated according to internal environment evolution
        and user interaction. The update is done at the end of the step right before returning observations.
        To update the boxes, we proceed in the following way:

        1. Only unopened boxes are considered for updates.
        2. If the box is considered active, we verify whether it was considered ready during its previous state.
            If this is the case, the box is deactivated.
            Note: The box becomes ready at the end of the update. If between the previous update and the current one
            it has not been opened, the button-press opportunity interval has passed, and it must be deactivated.
        3. We immediately verify if the box is deactivated and check if the current time has passed the chest
            re-activation time (re-activation-time = deactivation time + delay). If this is the case, the chest is
            reactivated. Note: Checks are made immediately (*if* instead of *else if*) since a box can be deactivated and
            reactivated during the same update. For example, if a box has been ready and is deactivated, however, the next
            observed event during the internal step either belongs to the same box or ends after the box re-activation
            time, it will be immediately reactivated.
        4. We immediately check if the pattern has been satisfied and if this is the case, mark the box as ready.
            Note: Checks are made immediately (*if* instead of *else if*) since a box can pass from deactivated,
            to activated, to ready in one step. An example of this is a one-event only box. Once the box has been ready,
            it is marked as deactivated. However, the next observed event also belongs to the box, leading to
            reactivation. Since the box has only one event, it is also marked ready right away.

        :param signal: list, optional
            A list of signals indicating the state changes to apply to the box (default is None).
        """
        if signal is None:
            signal = []

        if not self.state["_open"]:
            if self.state["active"]:
                # if the box has been _ready it should be timed out
                if self.state["_ready"]:
                    self._deactivate()
            if not self.state["active"]:
                if "active" in signal:
                    self._activate()
            # otherwise, check if pattern has been satisfied
            if "satisfied" in signal:
                self._ready()
