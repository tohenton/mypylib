class LogStateMachine:
    """
    Utility class for parsing specific structure text.

    Properties:
    - states: A dict that stores all the defined state by define_state()
    - state_relations: A dict that stores relations between states.
    - current_state_name: A str variable that stores current state name of state-machine.
    - NOT_STARTED_STATE: An initial state. A initial value of current_state_name.
    """

    class LogStateMachineError(Exception):
        pass

    class State:
        """
        State class for state-machine

        Properties:
        - name: Name of state
        - state_format: Regexp that expresses state
        """

        def __init__(self, name, state_format):
            self.name = name
            self.state_format = state_format

        def __str__(self):
            return "<State instance for \"%s\">" % self.name

        def is_state(self, line):
            """
            Checking if 'line' matches this state or not
            """

            return self.get_matcher(line) is not None

        def get_matcher(self, line):
            """
            Return matcher object that generated from 'state_format' and 'line'
            """

            return re.match(self.state_format, line)

    NOT_STARTED_STATE = "__not_started_state__%d" % randint(sys.maxint / 2, sys.maxint)

    def __init__(self):
        # Initialize properties
        self.states = dict()
        self.state_relations = dict()
        self.state_counts = dict()

        self.current_state_name = self.NOT_STARTED_STATE  # Set the initial state

        # Initialization for NOT_STARTED_STATE
        self.states[self.NOT_STARTED_STATE] = None  # Set dummy value for initial state
        self.state_relations[self.NOT_STARTED_STATE] = list()  # Set initial empty list for initial state

    def reset(self):
        """
        Reset LogStateMachine progresses.
        Note that it will not reset state definitions.
        """

        # Reset current state to the initial state
        self.current_state_name = self.NOT_STARTED_STATE

        # Reset all the state counts to zero
        for state in self.state_counts.keys():
            self.state_counts[state] = 0

    def define_state(self, name, state_format):
        """
        Define a new state.
        Arguments:
        - name: The name of new state.
        - state_format: The regexp that expresses new state

        Return:
          A State instance of the new state.

        Exception:
        - LogStateMachineError
          - In case if name is not an instance of str.
          - In case if state_format is not an instance of str.
          - In case if name is same as an already defined state name.
        """

        # Validations
        if not isinstance(name, str):
            raise self.LogStateMachineError("Invalid argument type (\"name\" (%s) is not 'str')" % type(name))
        if not isinstance(state_format, str):
            raise self.LogStateMachineError("Invalid argument type (\"state_format\" (%s) is not 'str')" % type(state_format))

        if name in self.states:
            raise self.LogStateMachineError("Already defined state (\"%s\")" % name)

        # Create the new state
        state = self.State(name, state_format)

        # Register the new state to states
        self.states[state.name] = state
        self.state_relations[state.name] = list()  # Set initial empty list for the new state
        self.state_counts[state.name] = 0

        return state

    def define_next(self, source_state, dest_state):
        """
        Define the relation between two states

        Arguments:
        - source_state: A State instance of the start side state of the relation
        - dest_state: A State instance of the next side state of the relation

        Return:
          None

        Exception:
        - LogStateMachineError
          - In case if dest_state is not an instance of State.
          - In case if source_state is not registered in LogStateMachine. (unlikely case)
          - In case if dest_state   is not registered in LogStateMachine. (unlikely case)
          - In case if source_state is not an instanf of State nor None.
        """

        # source_state validation
        if not isinstance(source_state, (self.State, type(None))):
            raise self.LogStateMachineError("Invalid source_state (\"%s\")" % type(source_state))
        if source_state and source_state.name not in self.states:
            raise self.LogStateMachineError("Undefined source_state (\"%s\")" % source_state.name)

        # dest_state validation
        if not isinstance(dest_state, self.State):
            raise self.LogStateMachineError("Invalid dest_state (\"%s\")" % type(dest_state))
        if dest_state.name not in self.states:
            raise self.LogStateMachineError("Undefined dest_state (\"%s\")" % dest_state.name)

        if source_state is None:
            self.state_relations[self.NOT_STARTED_STATE].append(dest_state.name)
        else:
            self.state_relations[source_state.name].append(dest_state.name)

    def forward_state(self, line):
        """
        Forward state-machine with 'line'.

        This method searches appropriate state with line from 'states'.
        If there is no state of current state, this method just returns None.
        If the appropriate state is found, update 'current_state_name' with its name and increment corresponding 'state_counts' entry.

        Argument:
        - line: An input for state-machine

        Exception:
        - LogStateMachineError
          - In case if there is no next state is defined for the initial state.
          - In case if there are one or more state if found with 'line'.
          - In case if there are one or more next state is defined, but no state is found with 'line'.
        """

        if len(self.state_relations[self.NOT_STARTED_STATE]) is 0:
            raise self.LogStateMachineError("No initial state defined yet")

        # Is last state?
        if len(self.state_relations[self.current_state_name]) is 0:
            # No more state
            return None

        next_state_names = filter(lambda state_name: self.states[state_name].is_state(line),
                                  self.state_relations[self.current_state_name])
        if len(next_state_names) > 1:
            raise self.LogStateMachineError("Wrong state (too many state found)")
        elif len(next_state_names) == 0:
            raise self.LogStateMachineError("Wrong state (no state found)")

        next_state_name = next_state_names[0]

        self.current_state_name = self.states[next_state_name].name
        self.state_counts[self.current_state_name] += 1
        return self.states[self.current_state_name]

    def state_count(self, state):
        """
        Return the count that state progressed
        """

        # Validation
        if not isinstance(state, self.State):
            raise self.LogStateMachineError("Invalid state (\"%s\")" % type(state))
        if state.name not in self.states:
            raise self.LogStateMachineError("Undefined state (\"%s\")" % state.name)

        return self.state_counts[state.name]

    def current_state(self):
        return self.states[self.current_state_name]

