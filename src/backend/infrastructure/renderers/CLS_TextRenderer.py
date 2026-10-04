from ...domain.DUT.STRUCT.ST_JobLayout import ST_JobLayout
from ...domain.DUT.STRUCT.ST_BackendToFrontendData import ST_BackendToFrontendData
from ...domain.DUT.ENUM.E_FileType import E_FileType


class CLS_TextRenderer:
    # Validate UTF-8 text without creating a display surface.
    def load(self, file_path: str) -> bool:
        try:
            with open(file_path, "r", encoding="utf-8-sig") as resource:
                while resource.read(8192):
                    pass
            return True
        except (OSError, ValueError):
            return False

    # Prepare the frontend contract without sending it yet.
    def render(
        self,
        stJobLayout: ST_JobLayout,
        *,
        section_id: str,
        file_name:  str,
        file_path:  str,
        file_type:  E_FileType,
    ) -> ST_BackendToFrontendData:
        return ST_BackendToFrontendData(
            file_type  = file_type,
            section_id     = section_id,
            file_name      = file_name,
            file_path      = file_path,
            stJobLayout    = stJobLayout,
        )
