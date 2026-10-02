from dataclasses          import dataclass

from ..ENUM.E_CommandType import E_CommandType

@dataclass
class ST_Command:
    command_type: E_CommandType
    file_name:    str
    file_path:    str
