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
