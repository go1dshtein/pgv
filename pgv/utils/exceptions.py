class PGVError(RuntimeError):
    pass


class PGVIsNotInitialized(PGVError):
    code = 1

    def __init__(self):
        message = "database is not initialized for working with pgv"
        super(PGVError, self).__init__(message)


class PGVUnknownCommand(PGVError):
    code = 2

    def __init__(self, command):
        message = "unknown command %s:" % command
        super(PGVError, self).__init__(message)
