from ..domain.CLS_ViewSection import CLS_ViewSection


# Manage active view sections and their section IDs.
class CLS_SectionManager:
    def __init__(self) -> None:
        # Map each section ID to its CLS_ViewSection instance.
        self._sections: dict[str, CLS_ViewSection] = {}

    @property
    def sections(self) -> dict[str, CLS_ViewSection]:
        # Access active sections by their IDs.
        return self._sections

    # Public operations will be implemented later.
    def initialize(self) -> None:
        pass

    # Create a section for a file and return its unique section ID.
    def create_section(self, file_name: str, file_path: str) -> str:
        pass

    # Return the section with this ID, or None if it does not exist.
    def get_section(self, section_id: str) -> CLS_ViewSection | None:
        pass

    # Return an existing section ID for reuse, or None if no section matches.
    # Both file name and file path must match to identify the same file.
    def find_section(self, file_name: str, file_path: str) -> str | None:
        pass

    def remove_section(self, section_id: str) -> None:
        pass

    def clear_sections(self) -> None:
        pass

    def reset(self) -> None:
        pass
