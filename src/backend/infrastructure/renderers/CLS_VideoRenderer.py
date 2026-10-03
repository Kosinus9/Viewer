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
