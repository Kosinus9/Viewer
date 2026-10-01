from ..domain.DUT.ENUM.E_CommandType import E_CommandType
from ..domain.DUT.STRUCT.ST_Command  import ST_Command


class CLS_CommandManager:
    def create_open_command(self, file_path: str) -> ST_Command:
        return ST_Command(
            command_type = E_CommandType.OPEN,
            file_path    = file_path,
        )
