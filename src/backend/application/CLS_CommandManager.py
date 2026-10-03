from ..domain.DUT.ENUM.E_CommandType import E_CommandType
from ..domain.DUT.STRUCT.ST_Command  import ST_Command
from pathlib                       import Path


class CLS_CommandManager:
    def create_open_command(self, file_path: str) -> ST_Command:
        st_command = ST_Command(
            command_type = E_CommandType.OPEN,
            file_name    = Path(file_path).name,
            file_path    = file_path,
        )
        print(
            "\n[TRACE TEMP][CommandManager] ST_Command cree\n"
            f"  command_type : {st_command.command_type.name}\n"
            "  section_id   : non attribue avant create_job()\n"
            f"  file_name    : {st_command.file_name}\n"
            f"  file_path    : {st_command.file_path}\n"
        )
        return st_command
