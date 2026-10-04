from ...domain.DUT.STRUCT.ST_JobLayout import ST_JobLayout


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

    # Frontend rendering will be connected in a later step.
    def render(self, stJobLayout: ST_JobLayout) -> None:
        pass
