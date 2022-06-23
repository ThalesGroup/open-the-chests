from Elements.Pattern import Pattern


class InteractiveBox:
    def __init__(self, id: int, pattern: Pattern = None, verbose=True):
        """
        An openable box that allows interaction. It possesses three states indicators: open, ready and active.
        The box is initialised with a pattern which defines when the box changes states.
        TODO: add reactivate after timeout

        :param verbose:
        :param id: id of box from 0 to (nb_boxes - 1)
        :param pattern: pattern object linked to box
        """
        self.verbose = verbose
        self.id = id
        self.box = {"open": False, "ready": False, "active": False}
        self.pattern = pattern

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

    def update(self):
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
