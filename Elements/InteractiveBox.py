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
        self.box = {"open": False, "ready": False, "active": False}
        self.pattern = pattern

    def reset(self, time):
        self.box = {"open": False, "ready": False, "active": False}
        self.activate()
        self.pattern.fill_event_stack(time)
        self.pattern.satisfied = False

    def is_open(self):
        return self.box["open"]

    def is_active(self):
        return self.box["active"]

    def open(self):
        """
        Opens box, deactivates it once it is opened and marks it as not ready
        """
        if self.verbose:
            print(f"Opening box {self.id}")
        self.box["open"] = True
        self.box["ready"] = False
        self.box["active"] = False

    def activate(self):
        """
        Activates box, marks it as not ready and not opened
        """
        assert not self.box["open"], "Cannot activate an opened box"
        assert not self.box["ready"], "Newly activated boxes shouldn't be ready"

        if self.verbose:
            print(f"Activating box {self.id}")

        self.box["active"] = True
        self.box["ready"] = False
        self.box["open"] = False

    def deactivate(self):
        """
        Deactivates box, marks it as not ready and not open
        """
        if self.verbose:
            print(f"Deactivating box {self.id}")

        self.box["active"] = False
        self.box["ready"] = False
        self.box["open"] = False
        self.pattern.satisfied = False

    def ready(self):
        """
        Makes box ready to open, removes active status
        """
        if self.verbose:
            print(f"Ready box {self.id}")

        self.box["active"] = True
        self.box["ready"] = True
        self.box["open"] = False

    def check_pattern(self):
        """

        """
        if self.pattern.satisfied:
            self.ready()

    def press_button(self):
        """
        Attempt to open box via button press. If box is active and ready it will open.
        :return: success of attempt
        """
        if not self.box["open"]:  # if the box has not been opened already
            if self.box["active"] and self.box["ready"]:  # if the box is active and ready to open
                self.open()
                return True
        return False  # in all other cases return false

    def update(self, t_current):
        """
        Verifies bos state and updates its status
        """
        if not self.box["open"]:
            if self.box["active"]:
                # if the box has been ready it should be timed out
                if self.box["ready"]:
                    self.deactivate()
                # otherwise, check if pattern has been satisfied
                else:
                    self.check_pattern()
            if not self.box["active"]:
                # TODO (priority 2) see if this can be moved somewhere else, not very clear
                if t_current >= self.pattern.start_pattern_time:
                    self.activate()
