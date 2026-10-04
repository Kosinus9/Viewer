from ...domain.DUT.STRUCT.ST_JobLayout import ST_JobLayout
from ...domain.DUT.STRUCT.ST_BackendToFrontendData import ST_BackendToFrontendData
from ...domain.DUT.ENUM.E_FileType import E_FileType


class CLS_VideoRenderer:
    # Check container signatures without preparing playback.
    def load(self, file_path: str) -> bool:
        try:
            with open(file_path, "rb") as resource:
                header = resource.read(12)
            return (
                header.startswith(b"\x1a\x45\xdf\xa3")
                or (len(header) == 12 and header[:4] == b"RIFF" and header[8:12] == b"AVI ")
                or (len(header) == 12 and header[4:8] in (b"ftyp", b"moov", b"mdat", b"wide"))
            )
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
            renderer_name  = file_type,
            section_id     = section_id,
            file_name      = file_name,
            file_path      = file_path,
            stJobLayout    = stJobLayout,
        )
