from enum import Enum


class E_ViewSectionState(Enum):
    LOADING    = "loading"
    VISIBLE    = "visible"
    BACKGROUND = "background"
    ERROR      = "error"
    CLOSING    = "closing"
    CLOSED     = "closed"
