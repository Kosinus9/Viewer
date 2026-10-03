from ..domain.CLS_ViewSection               import CLS_ViewSection
from ..domain.DUT.STRUCT.ST_Job             import ST_Job
from ..domain.DUT.STRUCT.ST_JobLayout       import ST_JobLayout
from ..domain.DUT.ENUM.E_ViewSectionState   import E_ViewSectionState
from .CLS_LayoutManager                     import CLS_LayoutManager


# Manage active view sections and their section IDs.
class CLS_SectionManager:
    def __init__(self, clsLayoutManager: CLS_LayoutManager) -> None:
        self._clsLayoutManager = clsLayoutManager
        # Map each section ID to its CLS_ViewSection instance.
        self._view_sections: dict[str, CLS_ViewSection] = {}

    @property
    def view_sections(self) -> dict[str, CLS_ViewSection]:
        # Access active CLS_ViewSection instances by their section IDs.
        return self._view_sections

    # Register a section using the ID already supplied by the Job.
    def create_section(self, stJob: ST_Job) -> str:
        print(
            "\n[TRACE TEMP][SectionManager] create_section() reçoit le ST_Job\n"
            f"  command_type : {stJob.command_type.name}\n"
            "\n  Section:\n"
            f"    section_id : {stJob.stJobSection.section_id}\n"
            f"    file_name  : {stJob.stJobSection.file_name}\n"
            f"    file_path  : {stJob.stJobSection.file_path}\n"
            "\n  Layout:\n"
            f"    position_x : {stJob.stJobLayout.position_x}\n"
            f"    position_y : {stJob.stJobLayout.position_y}\n"
            f"    width      : {stJob.stJobLayout.width}\n"
            f"    height     : {stJob.stJobLayout.height}\n"
            "\n  Lifecycle:\n"
            f"    duration         : {stJob.stJobLifecycle.duration}\n"
            f"    ignore_lifecycle : {stJob.stJobLifecycle.ignore_lifecycle}\n"
        )
        stJobSection = stJob.stJobSection
        section_id   = stJobSection.section_id
        if not isinstance(section_id, str) or not section_id:
            print("[TRACE TEMP][SectionManager] Rejet : section_id invalide")
            raise ValueError("Job requires a non-empty section_id.")
        if section_id in self._view_sections:
            print("[TRACE TEMP][SectionManager] Rejet : section_id deja enregistre")
            raise ValueError("section_id is already registered.")

        print("[TRACE TEMP][SectionManager] section_id accepte")
        print(f"[TRACE TEMP][SectionManager] Construction de CLS_ViewSection : section_id={section_id}")
        clsViewSection = CLS_ViewSection(
            section_id = section_id,
            file_name  = stJobSection.file_name,
            file_path  = stJobSection.file_path,
        )
        self._view_sections[section_id] = clsViewSection
        clsViewSection.initialize()

        print(
            "[TRACE TEMP][SectionManager] Section créée et enregistrée dans _view_sections\n"
            f"  section_id : {section_id}\n"
        )
        print("[TRACE TEMP][SectionManager] create_section() retourne section_id\n")
        return section_id

    # Return the section with this ID, or None if it does not exist.
    def get_section(self, section_id: str) -> CLS_ViewSection | None:
        return self._view_sections.get(section_id)

    # Delegate the show request when the section exists.
    def show_section(self, section_id: str) -> None:
        clsViewSection = self.get_section(section_id)
        if clsViewSection is not None:
            clsViewSection.show()
            self.update_layout()

    # Delegate the hide request when the section exists.
    def hide_section(self, section_id: str) -> None:
        clsViewSection = self.get_section(section_id)
        if clsViewSection is not None:
            clsViewSection.hide()
            self.update_layout()

    # Request closure, then remove the section from the registry.
    def close_section(self, section_id: str) -> None:
        clsViewSection = self.get_section(section_id)
        if clsViewSection is not None:
            clsViewSection.close()
            # Removal follows the synchronous return of close().
            self.remove_section(section_id)
            self.update_layout()

    # Only visible sections participate in layout calculation.
    def get_number_of_active_section(self) -> int:
        number_of_active_section = 0
        for clsViewSection in self._view_sections.values():
            if clsViewSection.state == E_ViewSectionState.VISIBLE:
                number_of_active_section += 1
        return number_of_active_section

    # Calculate geometry without assigning it to sections yet.
    def update_layout(self) -> list[ST_JobLayout] | None:
        number_of_active_section = self.get_number_of_active_section()
        if number_of_active_section == 0:
            return []
        return self._clsLayoutManager.calculate_layouts(number_of_active_section)

    # Return an existing section ID for reuse, or None if no section matches.
    # Both file name and file path must match to identify the same file.
    def find_section(self, file_name: str, file_path: str) -> str | None:
        for section_id, clsViewSection in self._view_sections.items():
            if clsViewSection.file_name == file_name and clsViewSection.file_path == file_path:
                return section_id
        return None

    # Unregister a section without invoking its resource cleanup.
    def remove_section(self, section_id: str) -> None:
        self._view_sections.pop(section_id, None)

    # Clear the registry without requesting individual section closures.
    def clear_sections(self) -> None:
        self._view_sections.clear()

    # Reset the manager by clearing its section registry.
    def reset(self) -> None:
        self.clear_sections()
