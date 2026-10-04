
from ..domain.DUT.STRUCT.ST_Job                     import ST_Job
from ..domain.DUT.STRUCT.ST_JobLayout               import ST_JobLayout
from ..domain.DUT.STRUCT.ST_BackendToFrontendData   import ST_BackendToFrontendData

from ..domain.DUT.ENUM.E_ViewSectionState           import E_ViewSectionState

from .CLS_LayoutManager                             import CLS_LayoutManager
from ..domain.CLS_ViewSection                       import CLS_ViewSection


# Manage active view sections and their section IDs.
class CLS_SectionManager:
    def __init__(self, clsLayoutManager: CLS_LayoutManager) -> None:
        self._clsLayoutManager = clsLayoutManager
        # Map each section ID to its CLS_ViewSection instance.
        self._view_sections:            dict[str, CLS_ViewSection]          = {}
        self._stJobLayouts:             dict[str, ST_JobLayout]             = {}
        self._stBackendToFrontendData:  dict[str, ST_BackendToFrontendData] = {}

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
        if clsViewSection.state == E_ViewSectionState.LOADING:
            self.on_section_loaded(section_id)
        return section_id

    # Apply the visibility policy after successful resource loading.
    def on_section_loaded(self, section_id: str) -> None:
        clsViewSection = self.get_section(section_id)
        if clsViewSection is not None and clsViewSection.state == E_ViewSectionState.LOADING:
            number_of_active_section = self.get_number_of_active_section()
            if number_of_active_section < 4:
                self.show_section(section_id)
            else:
                clsViewSection.background()
        
    # Delegate the show request when the section exists.
    def show_section(self, section_id: str) -> None:
        clsViewSection = self.get_section(section_id)
        if clsViewSection is not None:
            if clsViewSection.state not in (E_ViewSectionState.LOADING, E_ViewSectionState.BACKGROUND):
                return
            if self.get_number_of_active_section() >= 4:
                return
            stJobLayouts = self._recompute_layouts_if_needed(clsViewSection)
            if stJobLayouts is None:
                return
            stBackendToFrontendData = clsViewSection.show(self._stJobLayouts[section_id])
            if stBackendToFrontendData is not None:
                self._stBackendToFrontendData[section_id] = stBackendToFrontendData

    def get_backend_to_frontend_data(self) -> list[ST_BackendToFrontendData]:
        return [
            self._stBackendToFrontendData[section_id]
            for section_id in self._stJobLayouts
            if section_id in self._stBackendToFrontendData
            and self._view_sections[section_id].state == E_ViewSectionState.VISIBLE
        ]

    # Return the section with this ID, or None if it does not exist.
    def get_section(self, section_id: str) -> CLS_ViewSection | None:
        return self._view_sections.get(section_id)


    # Delegate the hide request when the section exists.
    def hide_section(self, section_id: str) -> None:
        clsViewSection = self.get_section(section_id)
        if clsViewSection is not None:
            previous_state = clsViewSection.state
            clsViewSection.hide()
            if clsViewSection.state != previous_state:
                self.update_layout()

    # Request closure, then remove the section from the registry.
    def close_section(self, section_id: str) -> None:
        clsViewSection = self.get_section(section_id)
        if clsViewSection is not None:
            was_visible = clsViewSection.state == E_ViewSectionState.VISIBLE
            clsViewSection.close()
            # Removal follows the synchronous return of close().
            self.remove_section(section_id)
            if was_visible:
                self.update_layout()

    # Only visible sections participate in layout calculation.
    def get_number_of_active_section(self) -> int:
        number_of_active_section = 0
        for clsViewSection in self._view_sections.values():
            if clsViewSection.state == E_ViewSectionState.VISIBLE:
                number_of_active_section += 1
        return number_of_active_section

    # Keep the existing calculation result while updating section associations.
    def update_layout(self) -> list[ST_JobLayout] | None:
        return self._recompute_layouts_if_needed()

    # Registry order determines the order of visible windows.
    def _recompute_layouts_if_needed(self, clsTargetViewSection: CLS_ViewSection | None = None) -> list[ST_JobLayout] | None:
        clsVisibleViewSections = [
            clsViewSection for clsViewSection in self._view_sections.values()
            if clsViewSection.state == E_ViewSectionState.VISIBLE or clsViewSection is clsTargetViewSection
        ]
        number_of_active_section = len(clsVisibleViewSections)
        if number_of_active_section == 0:
            self._map_layouts_to_visible_sections([], [])
            return []
        stJobLayouts = self._clsLayoutManager.calculate_layouts(number_of_active_section)
        if stJobLayouts is None:
            self._map_layouts_to_visible_sections([], [])
            return None
        self._map_layouts_to_visible_sections(clsVisibleViewSections, stJobLayouts)
        # Refresh prepared data for sections that were already visible.
        for clsViewSection in clsVisibleViewSections:
            if clsViewSection.state == E_ViewSectionState.VISIBLE:
                stBackendToFrontendData = clsViewSection.send_layout_to_renderer_for_display(
                    self._stJobLayouts[clsViewSection.section_id]
                )
                if stBackendToFrontendData is not None:
                    self._stBackendToFrontendData[clsViewSection.section_id] = stBackendToFrontendData
        return stJobLayouts

    # Replace the mapping so hidden or removed sections cannot keep a layout.
    def _map_layouts_to_visible_sections(
        self,
        clsVisibleViewSections: list[CLS_ViewSection],
        stJobLayouts: list[ST_JobLayout],
    ) -> None:
        self._stJobLayouts = {
            clsViewSection.section_id: stJobLayout
            for clsViewSection, stJobLayout in zip(clsVisibleViewSections, stJobLayouts, strict=True)
        }
        self._stBackendToFrontendData = {
            section_id: stBackendToFrontendData
            for section_id, stBackendToFrontendData in self._stBackendToFrontendData.items()
            if section_id in self._stJobLayouts
        }

    # Return an existing section ID for reuse, or None if no section matches.
    # Both file name and file path must match to identify the same file.
    def find_section(self, file_name: str, file_path: str) -> str | None:
        for section_id, clsViewSection in self._view_sections.items():
            if clsViewSection.file_name == file_name and clsViewSection.file_path == file_path:
                return section_id
        return None

    # Unregister a section without invoking its resource cleanup.
    def remove_section(self, section_id: str) -> None:
        clsViewSection = self._view_sections.pop(section_id, None)
        self._stJobLayouts.pop(section_id, None)
        self._stBackendToFrontendData.pop(section_id, None)
        if clsViewSection is not None and clsViewSection.state == E_ViewSectionState.VISIBLE:
            self.update_layout()

    # Clear the registry without requesting individual section closures.
    def clear_sections(self) -> None:
        self._view_sections.clear()
        self._stJobLayouts.clear()
        self._stBackendToFrontendData.clear()

    # Reset the manager by clearing its section registry.
    def reset(self) -> None:
        self.clear_sections()
