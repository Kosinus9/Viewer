from pathlib                                      import Path

from .DUT.ENUM.E_FileType                         import E_FileType
from .DUT.ENUM.E_ViewSectionState                 import E_ViewSectionState
from ..infrastructure.renderers.CLS_PDFRenderer   import CLS_PDFRenderer
from ..infrastructure.renderers.CLS_ImageRenderer import CLS_ImageRenderer
from ..infrastructure.renderers.CLS_VideoRenderer import CLS_VideoRenderer
from ..infrastructure.renderers.CLS_TextRenderer  import CLS_TextRenderer

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

    # Select and retain the renderer without loading the resource.
    def initialize(self) -> None:
        extension = Path(self._file_path).suffix.lower()
        self._clsRenderer = None

        if extension == ".pdf":
            self._file_type = E_FileType.PDF
            self._clsRenderer = CLS_PDFRenderer()
        elif extension in (".jpg", ".jpeg", ".png", ".bmp", ".webp"):
            self._file_type = E_FileType.IMAGE
            self._clsRenderer = CLS_ImageRenderer()
        elif extension in (".mp4", ".avi", ".mkv", ".mov", ".webm"):
            self._file_type = E_FileType.VIDEO
            self._clsRenderer = CLS_VideoRenderer()
        elif extension in (".txt", ".text"):
            self._file_type = E_FileType.TEXT
            self._clsRenderer = CLS_TextRenderer()
        else:
            self._file_type = E_FileType.UNKNOWN

        if self._file_type != E_FileType.UNKNOWN:
            self.loading()
        else:
            self.error()

    # Allow visibility only from the background state.
    def show(self) -> None:
        if self._state == E_ViewSectionState.BACKGROUND:
            self.visible()

    # Allow hiding only from the visible state.
    def hide(self) -> None:
        if self._state == E_ViewSectionState.VISIBLE:
            self.background()

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

    # Loading state entry; resource loading is not implemented yet.
    def loading(self) -> None:
        self._state = E_ViewSectionState.LOADING

    # Visible state entry; window display is not implemented yet.
    def visible(self) -> None:
        self._state = E_ViewSectionState.VISIBLE

    # Background state entry; window hiding is not implemented yet.
    def background(self) -> None:
        self._state = E_ViewSectionState.BACKGROUND

    # Error state entry; error handling is not implemented yet.
    def error(self) -> None:
        self._state = E_ViewSectionState.ERROR

    # Closing state entry; cleanup and completion remain pending.
    def closing(self) -> None:
        self._state = E_ViewSectionState.CLOSING

    # Called when resource cleanup has actually completed.
    def closed(self) -> None:
        self._state = E_ViewSectionState.CLOSED

    # Return the section to its initial state. Not implemented yet.
    def reset(self) -> None:
        pass
