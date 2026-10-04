from ...domain.DUT.STRUCT.ST_JobLayout import ST_JobLayout


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

    # Frontend rendering will be connected in a later step.
    def render(self, stJobLayout: ST_JobLayout) -> None:
        pass
