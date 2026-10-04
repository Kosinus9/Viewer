from dataclasses import dataclass

from .ST_JobLayout import ST_JobLayout


@dataclass
class ST_BackendToFrontendData:
    renderer_name: str
    section_id:    str
    file_name:     str
    file_path:     str
    stJobLayout:   ST_JobLayout
