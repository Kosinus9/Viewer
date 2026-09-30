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

    # Prepare the section for use. Not implemented yet.
    def initialize(self) -> None:
        pass

    # Show the section. Not implemented yet.
    def show(self) -> None:
        pass

    # Hide the section. Not implemented yet.
    def hide(self) -> None:
        pass

    # Refresh the section content. Not implemented yet.
    def refresh(self) -> None:
        pass

    # Close the section. Not implemented yet.
    def close(self) -> None:
        pass

    # Return the section to its initial state. Not implemented yet.
    def reset(self) -> None:
        pass
