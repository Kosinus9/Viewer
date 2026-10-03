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
