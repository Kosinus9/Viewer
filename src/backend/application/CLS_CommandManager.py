from ..domain.DUT.ENUM.E_CommandType import E_CommandType
from ..domain.DUT.STRUCT.ST_Command  import ST_Command
from pathlib                       import Path


class CLS_CommandManager:
    def create_open_command(self, file_path: str) -> ST_Command:
        return ST_Command(
            command_type = E_CommandType.OPEN,
            file_name    = Path(file_path).name,
            file_path    = file_path,
        )
