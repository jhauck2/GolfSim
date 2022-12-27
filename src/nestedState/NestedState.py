from src.state import State


class NestedState(State):

    def __init__(self, name, default="", states=None, parent_state_machine=None):
        # default is the default state
        # state is the list of substates
        self.name = name
        if states is None:
            states = []
        self.default = default
        self.states = {}
        for state in states:
            if state.name not in self.states:
                self.states[state.name] = state  # add all the states to the state machine
                state.state_machine = self  # set the parent state machine of each state

        self.current = self.states[self.default]  # Set the current state to the default state

        super().__init__(self, parent_state_machine)

    def add_state(self, state):
        if state.name not in self.states:
            self.states[state.name] = state  # add all the states to the state machine
            state.state_machine = self  # set the parent state machine of each state

    def add_states(self, states):
        for state in states:
            if state.name not in self.states:
                self.states[state.name] = state  # add all the states to the state machine
                state.state_machine = self  # set the parent state machine of each state

    def update(self, delta):
        self.current.update(delta)

    def transition_to(self, new_state, msg=None):
        try:
            self.current.exit()
            self.current = self.states[new_state]
            self.current.enter(msg)
        except ValueError:
            pass

    def enter(self, msg=None):
        super().enter(msg)
        if "state" in msg:
            self.current = self.states[msg["state"]]
            msg.erase("state")
        else:
            self.current = self.states[self.default]
        if "msg" in msg:  # send sub-message which may have more sub states
            self.current.enter(msg["msg"])
        else:
            self.current.enter(msg)

    def exit(self, msg=None):
        self.current.exit(msg)
        super().exit(msg)
