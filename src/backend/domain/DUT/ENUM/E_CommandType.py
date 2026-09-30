from enum import Enum


# Shared command types carried by a Job.
class E_CommandType(Enum):
    OPEN  = "open"
    SHOW  = "show"
    HIDE  = "hide"
    CLOSE = "close"
    RESET = "reset"
