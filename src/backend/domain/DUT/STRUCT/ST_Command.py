from dataclasses          import dataclass

from ..ENUM.E_CommandType import E_CommandType

@dataclass
class ST_Command:
    command_type: E_CommandType
    section_id:   str | None = None
    file_path:    str | None = None
