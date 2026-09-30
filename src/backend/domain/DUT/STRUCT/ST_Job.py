from dataclasses import dataclass

from ..ENUM.E_CommandType   import E_CommandType
from .ST_JobSection         import ST_JobSection
from .ST_JobLayout          import ST_JobLayout
from .ST_JobLifecycle       import ST_JobLifecycle


@dataclass
class ST_Job:
    command_type:   E_CommandType
    stJobSection:   ST_JobSection
    stJobLayout:    ST_JobLayout
    stJobLifecycle: ST_JobLifecycle
