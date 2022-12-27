from src.subject import Subject


class State(Subject):
    def __init__(self, name, parent_state_machine=None):
        super().__init__()
        self.name = name
        self.state_machine = parent_state_machine
        self.is_active = False

    def update(self, delta):
        pass

    def enter(self, msg=None):
        self.notify("entered")
        self.is_active = True

    def exit(self, msg=None):
        self.notify("exited")
        self.is_active = False
