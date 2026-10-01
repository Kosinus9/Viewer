from ..domain.DUT.ENUM.E_CommandType import E_CommandType
from ..domain.DUT.STRUCT.ST_Command import ST_Command


class CLS_Command:
    def create_open_command(self, file_path: str) -> ST_Command:
        return ST_Command(
            command_type = E_CommandType.OPEN,
            section_id   = None,
            file_path    = file_path,
        )

    def create_show_command(self, section_id: str) -> ST_Command:
        return ST_Command(
            command_type = E_CommandType.SHOW,
            section_id   = section_id,
            file_path    = None,
        )

    def create_hide_command(self, section_id: str) -> ST_Command:
        return ST_Command(
            command_type = E_CommandType.HIDE,
            section_id   = section_id,
            file_path    = None,
        )

    def create_close_command(self, section_id: str) -> ST_Command:
        return ST_Command(
            command_type = E_CommandType.CLOSE,
            section_id   = section_id,
            file_path    = None,
        )
