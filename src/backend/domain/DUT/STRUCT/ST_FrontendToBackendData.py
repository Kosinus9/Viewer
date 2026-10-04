from dataclasses import dataclass


@dataclass
class ST_FrontendToBackendData:
    section_id: str
    event:      str
