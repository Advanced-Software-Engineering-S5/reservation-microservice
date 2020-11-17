"""This module contains the project-defined exceptions
"""

class GoOutSafeError(Exception):
    pass

class DatabaseError(GoOutSafeError):
    pass

class UserNotInDB(GoOutSafeError):
    pass

class FormValidationError(GoOutSafeError):
    pass