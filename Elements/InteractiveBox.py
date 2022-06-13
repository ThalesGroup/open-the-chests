from Elements.Pattern import Pattern


class InteractiveBox:
    def __init__(self, id: int, pattern: Pattern = None):
        self.id = id
        self.box = { "open": False, "ready": False, "active": True}
        self.pattern = Pattern

    def press_button(self):
        opened = False
        if not self.box["open"]:
            opened = self.box["active"] and self.box["ready"]
            self.box["open"] = opened
        return opened

    def activate(self):
        assert not self.box["open"], "Cannot activate an opened box"
        assert not self.box["ready"], "Newly activated boxes shouldn't be ready"
        self.box["active"] = True

    def update(self):
        if not self.box["open"]:
            if self.box["active"]:
                # if the box has been ready it should be timed out
                if self.box["ready"]:
                    self.box["active"] = False
                    self.box["ready"] = False
                # otherwise, check if pattern has been satisfied
                else:
                    self.box["ready"] = self.pattern.satisfied
