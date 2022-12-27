from src.subject import Subject
import time


class StateMachine(Subject):

    def __init__(self, default="", states=None):
        # default is the default state
        # state is the list of substates
        super().__init__()
        if states is None:
            states = []
        self.default = default
        self.states = {}
        self.time = time.time()
        for state in states:
            if state.name not in self.states:
                self.states[state.name] = state  # add all the states to the state machine
                state.state_machine = self  # set the parent state machine of each state

        self.current = self.states[self.default]  # Set the current state to the default state
        self.current.enter()

    def update(self):
        cur_time = time.time()
        delta = cur_time - self.time
        self.time = cur_time
        self.current.update(delta)

    def add_state(self, state):
        if state.name not in self.states:
            self.states[state.name] = state  # add all the states to the state machine
            state.state_machine = self  # set the parent state machine of each state

    def add_states(self, states):
        for state in states:
            if state.name not in self.states:
                self.states[state.name] = state  # add all the states to the state machine
                state.state_machine = self  # set the parent state machine of each state

    def transition_to(self, new_state, msg=None):
        try:
            self.current.exit()
            self.current = self.states[new_state]
            self.current.enter(msg)
        except ValueError:
            pass
