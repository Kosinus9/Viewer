from pathlib                                       import Path

from .DUT.ENUM.E_FileType                          import E_FileType
from .DUT.ENUM.E_ViewSectionState                  import E_ViewSectionState

from .DUT.STRUCT.ST_JobLayout                      import ST_JobLayout
from .DUT.STRUCT.ST_BackendToFrontendData          import ST_BackendToFrontendData

from ..infrastructure.renderers.CLS_PDFRenderer    import CLS_PDFRenderer
from ..infrastructure.renderers.CLS_ImageRenderer  import CLS_ImageRenderer
from ..infrastructure.renderers.CLS_VideoRenderer  import CLS_VideoRenderer
from ..infrastructure.renderers.CLS_TextRenderer   import CLS_TextRenderer

# Represent a single section managed by CLS_SectionManager.
class CLS_ViewSection:
    def __init__(
        self,
        section_id: str,
        file_name:  str,
        file_path:  str,
    ) -> None:
        # Store the section ID and file details provided by the caller.
        self._section_id:    str = section_id
        self._file_name:     str = file_name
        self._file_path:     str = file_path
        self._file_type:     E_FileType | None = None
        self._state:         E_ViewSectionState | None = None
        self._clsRenderer:   CLS_PDFRenderer | CLS_ImageRenderer | CLS_VideoRenderer | CLS_TextRenderer | None = None

    @property
    def section_id(self) -> str:
        # Return the ID provided by the section manager.
        return self._section_id

    @property
    def file_name(self) -> str:
        # Return the file name.
        return self._file_name

    @property
    def file_path(self) -> str:
        # Return the file path.
        return self._file_path

    @property
    def file_type(self) -> E_FileType | None:
        # Expose the detected type without allowing external changes.
        return self._file_type

    @property
    def state(self) -> E_ViewSectionState | None:
        # Expose the current state without allowing external changes.
        return self._state

    # Select and retain the renderer before delegating resource loading.
    def initialize(self) -> None:
        print(
            f"[TRACE TEMP][ViewSection] initialize() section_id={self._section_id} "
            f"file_name={self._file_name} file_path={self._file_path} state={self._state}"
        )
        extension = Path(self._file_path).suffix.lower()
        print(f"[TRACE TEMP][ViewSection] section_id={self._section_id} extension={extension!r}")
        self._clsRenderer = None

        if extension == ".pdf":
            self._file_type   = E_FileType.PDF
            self._clsRenderer = CLS_PDFRenderer()
        elif extension in (".jpg", ".jpeg", ".png", ".bmp", ".webp"):
            self._file_type   = E_FileType.IMAGE
            self._clsRenderer = CLS_ImageRenderer()
        elif extension in (".mp4", ".avi", ".mkv", ".mov", ".webm"):
            self._file_type   = E_FileType.VIDEO
            self._clsRenderer = CLS_VideoRenderer()
        elif extension in (".txt", ".text"):
            self._file_type   = E_FileType.TEXT
            self._clsRenderer = CLS_TextRenderer()
        else:
            self._file_type   = E_FileType.UNKNOWN

        print(
            f"[TRACE TEMP][ViewSection] section_id={self._section_id} file_type={self._file_type} "
            f"renderer={type(self._clsRenderer).__name__ if self._clsRenderer is not None else 'None'}"
        )
        if self._file_type != E_FileType.UNKNOWN:
            self.loading()
        else:
            self.error()
        print(f"[TRACE TEMP][ViewSection] section_id={self._section_id} initialize() termine state={self._state}")

    # Leave successful loading in LOADING for SectionManager's visibility decision.
    def loading(self) -> None:
        self._state = E_ViewSectionState.LOADING
        if self._clsRenderer is None:
            self.error()
            return
        loading_success = self._clsRenderer.load(self._file_path)
        print(f"[TRACE TEMP][ViewSection] section_id={self._section_id} load() success={loading_success}")
        if not loading_success:
            self.error()

    # Visible state entry; window display is not implemented yet.
    def visible(self) -> None:
        self._state = E_ViewSectionState.VISIBLE

    # Background state entry; window hiding is not implemented yet.
    def background(self) -> None:
        self._state = E_ViewSectionState.BACKGROUND

    # Error state entry; error handling is not implemented yet.
    def error(self) -> None:
        self._state = E_ViewSectionState.ERROR

    # Allow visibility after loading or while returning from the background.
    def show(self, stJobLayout: ST_JobLayout) -> ST_BackendToFrontendData | None:
        previous_state = self._state
        stBackendToFrontendData = None
        if self._state in (E_ViewSectionState.LOADING, E_ViewSectionState.BACKGROUND):
            self.visible()
            stBackendToFrontendData = self.send_layout_to_renderer_for_display(stJobLayout)
        print(f"[TRACE TEMP][ViewSection] section_id={self._section_id} SHOW {previous_state} -> {self._state}")
        return stBackendToFrontendData


    # Forward the layout to the renderer already owned by this section.
    def send_layout_to_renderer_for_display(self, stJobLayout: ST_JobLayout) -> ST_BackendToFrontendData | None:
        if self._clsRenderer is not None:
            return self._clsRenderer.render(
                stJobLayout,
                section_id     = self._section_id,
                file_name      = self._file_name,
                file_path      = self._file_path,
                file_type      = self._file_type,
            )
        return None

    # Allow hiding only from the visible state.
    def hide(self) -> None:
        previous_state = self._state
        if self._state == E_ViewSectionState.VISIBLE:
            self.background()
        print(f"[TRACE TEMP][ViewSection] section_id={self._section_id} HIDE {previous_state} -> {self._state}")

    # Refresh the section content. Not implemented yet.
    def refresh(self) -> None:
        pass

    # Enter closing only from states that allow a close request.
    def close(self) -> None:
        if self._state in (
            E_ViewSectionState.VISIBLE,
            E_ViewSectionState.BACKGROUND,
            E_ViewSectionState.ERROR,
        ):
            self.closing()

    # Closing state entry; cleanup and completion remain pending.
    def closing(self) -> None:
        self._state = E_ViewSectionState.CLOSING

    # Called when resource cleanup has actually completed.
    def closed(self) -> None:
        self._state = E_ViewSectionState.CLOSED

    # Return the section to its initial state. Not implemented yet.
    def reset(self) -> None:
        pass
