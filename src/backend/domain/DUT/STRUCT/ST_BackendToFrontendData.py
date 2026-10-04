from dataclasses       import dataclass

from .ST_JobLayout     import ST_JobLayout
from ..ENUM.E_FileType import E_FileType

@dataclass
class ST_BackendToFrontendData:
    renderer_name: E_FileType
    section_id:    str
    file_name:     str
    file_path:     str
    stJobLayout:   ST_JobLayout
