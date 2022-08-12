from Elements.Pattern import Pattern

# TODO (priority 4) doc
from utils.utils import bug_print


class InteractiveBox:
    def __init__(self, id, pattern: Pattern = None, verbose=True):
        """
        An openable box that allows interaction.
        It possesses three states indicators: open, ready and active.
        The box is initialised with a pattern which defines how the box changes states.

        :param id:
        :param pattern: pattern object linked to box
        :param verbose:
        """
        self.id = id
        self.verbose = verbose
        # TODO (priority 3) rename this can cause confusion box.box?
        self.state = {"open": False, "ready": False, "active": False}
        self.pattern = pattern

    def get_state(self):
        return self.state

    def is_ready(self):
        return self.state["ready"]

    def is_open(self):
        return self.state["open"]

    def is_active(self):
        return self.state["active"]

    def check_pattern(self):
        """
        Check if box pattern has been fully displayed and change box state to ready if this is the case
        """
        if self.pattern.satisfied:
            self.ready()

    def reset(self, time):
        """
        Reset a box to initial conditions, not opened, not ready and active and regenerate its event stack starting
        at a selected time.
        :param time: The time to use as a start for the box pattern
        """
        self.state = {"open": False, "ready": False, "active": False}
        self.activate()
        self.pattern.fill_event_stack(time)
        # TODO (priority 3) can this be moved to some more pattern related place?
        self.pattern.satisfied = False

    def open(self):
        """
        Opens box, deactivates it once it is opened and marks it as not ready
        """
        if self.verbose:
            print(f"Opening box {self.id}")
        self.state["open"] = True
        self.state["ready"] = False
        self.state["active"] = False

    def activate(self):
        """
        Activates box, marks it as not ready and not opened
        """
        assert not self.state["open"], "Cannot activate an opened box"
        assert not self.state["ready"], "Newly activated boxes shouldn't be ready"

        if self.verbose:
            print(f"Activating box {self.id}")

        self.state["active"] = True
        self.state["ready"] = False
        self.state["open"] = False

    def deactivate(self):
        """
        Deactivates box, marks it as not ready and not open
        """
        if self.verbose:
            print(f"Deactivating box {self.id}")

        self.state["active"] = False
        self.state["ready"] = False
        self.state["open"] = False
        self.pattern.satisfied = False

    def ready(self):
        """
        Makes box ready to open, removes active status
        """
        if self.verbose:
            print(f"Ready box {self.id}")

        self.state["active"] = True
        self.state["ready"] = True
        self.state["open"] = False

    def press_button(self):
        """
        Attempt to open box via button press. If box is active and ready it will open.
        :return: success of attempt
        """
        if not self.state["open"]:  # if the box has not been opened already
            if self.state["active"] and self.state["ready"]:  # if the box is active and ready to open
                self.open()
                return True
        return False  # in all other cases return false

    def update(self, t_current):
        """
        Verifies bos state and updates its status
        """
        if not self.state["open"]:
            if self.state["active"]:
                # if the box has been ready it should be timed out
                if self.state["ready"]:
                    self.deactivate()
                # otherwise, check if pattern has been satisfied
                else:
                    self.check_pattern()
            if not self.state["active"]:
                # TODO (priority 3) see if this can be moved somewhere else, not very clear maybe?
                if t_current >= self.pattern.start_pattern_time:
                    self.activate()
