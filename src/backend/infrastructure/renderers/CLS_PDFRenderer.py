from ...domain.DUT.STRUCT.ST_JobLayout import ST_JobLayout
from ...domain.DUT.STRUCT.ST_BackendToFrontendData import ST_BackendToFrontendData
from ...domain.DUT.ENUM.E_FileType import E_FileType


class CLS_PDFRenderer:
    # Check the PDF header; full document parsing is deferred.
    def load(self, file_path: str) -> bool:
        try:
            with open(file_path, "rb") as resource:
                header = resource.read(8)
            return (
                len(header)     == 8
                and header[:5]  == b"%PDF-"
                and header[5:6] in (b"1", b"2")
                and header[6:7] == b"."
                and header[7:8].isdigit()
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
