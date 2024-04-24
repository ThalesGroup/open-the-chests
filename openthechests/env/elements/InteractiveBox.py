from openthechests.env.elements.Pattern import Pattern


# TODO (priority 4) doc
from openthechests.env.utils.helper_functions import bug_print


class InteractiveBox:
    def __init__(self,
                 id: int,
                 verbose: bool=True):
        """
        An openable box that allows interaction.
        It possesses three states indicators: _open, _ready and active.
        The box is initialised with a pattern which defines how the box changes states.

        :param id: The identifier of the box.
        :param verbose: Give details.
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
        Reset a box to initial conditions, not opened, not _ready and active and regenerate its event stack starting
        at a selected _time.
        """
        self.state = {"_open": False, "_ready": False, "active": False}
        self.num_deactivations = 0

    def _open(self):
        """
        Opens box, deactivates it once it is opened and marks it as not _ready
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
        Activates box, marks it as not _ready and not opened
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
        Deactivates box, marks it as not _ready and not _open
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
        Makes box _ready to _open, removes active status
        """
        assert self.state["active"], "Deactivated box cannot be _ready."

        if self.verbose:
            print(f"Ready box {self.id}")

        self.state["active"] = True
        self.state["_ready"] = True
        self.state["_open"] = False

    def press_button(self):
        """
        Attempt to _open box via button press. If box is active and _ready it will _open.
        :return: success of attempt
        """
        if not self.state["_open"]:  # if the box has not been opened already
            if self.state["active"] and self.state["_ready"]:  # if the box is active and _ready to _open
                self._open()
                return True
        return False  # in all other cases return false

    def update(self, signal=None):
        """
        Update box status using the current _time information.
        During each environment steps each box is updates according to internal environment evolution
        and user interaction. The update is done at the end of the step right before returning observations.
        To update the boxes we proceed in the following way:

        1. Only unopened boxes are considered for updates.
        2. If the box is considered as active, we verify whether it was considered as _ready during its previous state.
            If this is the case the box is deactivated.
            Note: The box becomes _ready at the end of the update. If between the previous update and the current one
            it has not been opened, the button-press opportunity interval has passed, and it must be deactivated.

        3. We immediately verify if the box is deactivated and check if the current _time has passed the chest
            re-activation _time (re-activation-_time = deactivation _time + delay). If this is the case the chest is
            reactivated. Note: Checks are made immediately (*if* instead *else if*) since a box can be deactivated and
            reactivated during the same update. For example, if a box has been _ready and is deactivated, however the next
            observed event during the internal step either belongs to the same box or ends after the box re-activation
            _time, it will be immediately reactivated.

        4. We immediately check if the pattern has been satisfied and if this is the case, mark the box as _ready.
            Note: Checks are made immediately (*if* instead *else if*) since a box can pass from deactivated,
            to activated to _ready in one step. An example of this is a one-event only box. Once the box has been _ready,
            it is marked as deactivated. However, the next observed event also belongs to the box, leading to
            reactivation. Since the box has only one event, it also marked _ready right away.

        :param signal:
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
