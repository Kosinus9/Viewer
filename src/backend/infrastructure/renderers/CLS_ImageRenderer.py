from ...domain.DUT.STRUCT.ST_JobLayout               import ST_JobLayout
from ...domain.DUT.STRUCT.ST_BackendToFrontendData   import ST_BackendToFrontendData
from ...domain.DUT.ENUM.E_FileType                   import E_FileType

class CLS_ImageRenderer:
    # Check supported image signatures without decoding pixels.
    def load(self, file_path: str) -> bool:
        try:
            with open(file_path, "rb") as resource:
                header = resource.read(12)
            return (
                header.startswith(b"\xff\xd8\xff")
                or header.startswith(b"\x89PNG\r\n\x1a\n")
                or header.startswith(b"BM")
                or (len(header) == 12 and header[:4] == b"RIFF" and header[8:12] == b"WEBP")
            )
        except (OSError, ValueError):
            return False

    # Prepare the frontend contract without sending it yet.
    def render(
        self,
        stJobLayout: ST_JobLayout,
        *,
        section_id:   str,
        file_name:    str,
        file_path:    str,
        file_type:    E_FileType,
    ) -> ST_BackendToFrontendData:
        return ST_BackendToFrontendData(
            file_type  = file_type,
            section_id     = section_id,
            file_name      = file_name,
            file_path      = file_path,
            stJobLayout    = stJobLayout,
        )
