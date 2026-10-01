from ..domain.CLS_ViewSection   import CLS_ViewSection
from ..domain.DUT.STRUCT.ST_Job import ST_Job


# Manage active view sections and their section IDs.
class CLS_SectionManager:
    def __init__(self) -> None:
        # Map each section ID to its CLS_ViewSection instance.
        self._sections: dict[str, CLS_ViewSection] = {}

    @property
    def sections(self) -> dict[str, CLS_ViewSection]:
        # Access active sections by their IDs.
        return self._sections

    # Initialization will be implemented later.
    def initialize(self) -> None:
        pass

    # Register a section using the ID already supplied by the Job.
    def create_section(self, stJob: ST_Job) -> str:
        stJobSection = stJob.stJobSection
        section_id   = stJobSection.section_id
        if not isinstance(section_id, str) or not section_id:
            raise ValueError("Job requires a non-empty section_id.")
        if section_id in self._sections:
            raise ValueError("section_id is already registered.")

        clsViewSection = CLS_ViewSection(
            section_id = section_id,
            file_name  = stJobSection.file_name,
            file_path  = stJobSection.file_path,
        )
        self._sections[section_id] = clsViewSection
        return section_id

    # Return the section with this ID, or None if it does not exist.
    def get_section(self, section_id: str) -> CLS_ViewSection | None:
        return self._sections.get(section_id)

    def show_section(self, section_id: str) -> None:
        clsViewSection = self.get_section(section_id)
        if clsViewSection is not None:
            clsViewSection.show()

    def hide_section(self, section_id: str) -> None:
        clsViewSection = self.get_section(section_id)
        if clsViewSection is not None:
            clsViewSection.hide()

    def close_section(self, section_id: str) -> None:
        clsViewSection = self.get_section(section_id)
        if clsViewSection is not None:
            clsViewSection.close()
            # Removal follows the synchronous return of close().
            self.remove_section(section_id)

    # Return an existing section ID for reuse, or None if no section matches.
    # Both file name and file path must match to identify the same file.
    def find_section(self, file_name: str, file_path: str) -> str | None:
        for section_id, clsViewSection in self._sections.items():
            if clsViewSection.file_name == file_name and clsViewSection.file_path == file_path:
                return section_id
        return None

    def remove_section(self, section_id: str) -> None:
        self._sections.pop(section_id, None)

    def clear_sections(self) -> None:
        self._sections.clear()

    def reset(self) -> None:
        self.clear_sections()
