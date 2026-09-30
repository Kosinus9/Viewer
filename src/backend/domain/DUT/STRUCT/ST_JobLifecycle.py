from dataclasses import dataclass


@dataclass
class ST_JobLifecycle:
    duration:          float | None = None
    ignore_lifecycle:  bool  = False
