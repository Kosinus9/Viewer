from enum import Enum

# Shared command types used by the Viewer.
class E_CommandType(Enum):
    OPEN  = "open"
    SHOW  = "show"
    HIDE  = "hide"
    CLOSE = "close"
    RESET = "reset"
