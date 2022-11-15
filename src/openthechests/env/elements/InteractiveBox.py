from src.openthechests.env.elements.Pattern import Pattern

# TODO (priority 4) doc


class InteractiveBox:
    def __init__(self, id, pattern: Pattern = None, verbose=True):
        """
        An openable box that allows interaction.
        It possesses three states indicators: open, ready and active.
        The box is initialised with a pattern which defines how the box changes states.

        :param id: The identifier of the box.
        :param pattern: Pattern object linked to box handling event tracking and generation.
        :param verbose: Give details.
        """
        self.id = id
        self.verbose = verbose
        # TODO (priority 3) rename this can cause confusion box.box?
        self.state = {"open": False, "ready": False, "active": False}
        self.pattern = pattern
        self.num_deactivations = 0

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
            # TODO (priority 3) can this be moved to some more pattern related place?
            self.pattern.satisfied = False
            self.ready()

    def reset(self, time):
        """
        Reset a box to initial conditions, not opened, not ready and active and regenerate its event stack starting
        at a selected time.
        :param time: The time to use as a start for the box pattern
        """
        self.state = {"open": False, "ready": False, "active": False}
        self.num_deactivations = 0
        self.activate()
        self.pattern.reset()

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

        self.num_deactivations += 1
        self.state["active"] = False
        self.state["ready"] = False
        self.state["open"] = False

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
        Update box status using the current time information.
        During each environment steps each box is updates according to internal environment evolution
        and user interaction. The update is done at the end of the step right before returning observations.
        To update the boxes we proceed in the following way:

        1. Only unopened boxes are considered for updates.
        2. If the box is considered as active, we verify whether it was considered as ready during its previous state.
            If this is the case the box is deactivated.
            Note: The box becomes ready at the end of the update. If between the previous update and the current one
            it has not been opened, the button-press opportunity interval has passed, and it must be deactivated.

        3. We immediately verify if the box is deactivated and check if the current time has passed the chest
            re-activation time (re-activation-time = deactivation time + delay). If this is the case the chest is
            reactivated. Note: Checks are made immediately (*if* instead *else if*) since a box can be deactivated and
            reactivated during the same update. For example, if a box has been ready and is deactivated, however the next
            observed event during the internal step either belongs to the same box or ends after the box re-activation
            time, it will be immediately reactivated.

        4. We immediately check if the pattern has been satisfied and if this is the case, mark the box as ready.
            Note: Checks are made immediately (*if* instead *else if*) since a box can pass from deactivated,
            to activated to ready in one step. An example of this is a one-event only box. Once the box has been ready,
            it is marked as deactivated. However, the next observed event also belongs to the box, leading to
            reactivation. Since the box has only one event, it also marked ready right away.

        :param t_current: The current time during the update, given by the last observed event, used for reactivating
                            the box.
        """
        if not self.state["open"]:
            if self.state["active"]:
                # if the box has been ready it should be timed out
                if self.state["ready"]:
                    self.deactivate()
            if not self.state["active"]:
                # TODO (priority 3) see if this can be moved somewhere else, not very clear maybe?
                if t_current >= self.pattern.start_pattern_time:
                    self.activate()
            # otherwise, check if pattern has been satisfied
            self.check_pattern()
