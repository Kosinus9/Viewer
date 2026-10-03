from pathlib                       import Path

from .DUT.ENUM.E_FileType          import E_FileType
from .DUT.ENUM.E_ViewSectionState  import E_ViewSectionState


# Represent a single section managed by CLS_SectionManager.
class CLS_ViewSection:
    def __init__(
        self,
        section_id: str,
        file_name:  str,
        file_path:  str,
    ) -> None:
        # Store the section ID and file details provided by the caller.
        self._section_id: str = section_id
        self._file_name:  str = file_name
        self._file_path:  str = file_path
        self._file_type:  E_FileType | None = None
        self._state:      E_ViewSectionState | None = None

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
        return self._file_type

    @property
    def state(self) -> E_ViewSectionState | None:
        return self._state

    def initialize(self) -> None:
        extension = Path(self._file_path).suffix.lower()
        self._file_type = E_FileType.PDF if extension == ".pdf" else E_FileType.ERROR
        self._state = (
            E_ViewSectionState.LOADING if self._file_type == E_FileType.PDF
            else E_ViewSectionState.ERROR
        )

    def show(self) -> None:
        if self._state == E_ViewSectionState.BACKGROUND:
            self._state = E_ViewSectionState.VISIBLE

    def hide(self) -> None:
        if self._state == E_ViewSectionState.VISIBLE:
            self._state = E_ViewSectionState.BACKGROUND

    # Refresh the section content. Not implemented yet.
    def refresh(self) -> None:
        pass

    def close(self) -> None:
        if self._state in (
            E_ViewSectionState.VISIBLE,
            E_ViewSectionState.BACKGROUND,
            E_ViewSectionState.ERROR,
        ):
            self._state = E_ViewSectionState.CLOSING
            self._state = E_ViewSectionState.CLOSED

    # Return the section to its initial state. Not implemented yet.
    def reset(self) -> None:
        pass
