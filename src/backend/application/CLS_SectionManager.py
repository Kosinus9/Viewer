from ..domain.CLS_ViewSection import CLS_ViewSection


# Manage the view sections used by the application.
class CLS_SectionManager:
    def __init__(self) -> None:
        self._sections: list[CLS_ViewSection] = []

    @property
    def sections(self) -> list[CLS_ViewSection]:
        # Access the current sections.
        return self._sections

    # Public operations will be implemented later.
    def initialize(self) -> None:
        pass

    def create_section(self) -> None:
        pass

    def get_section(self) -> None:
        pass

    def remove_section(self) -> None:
        pass

    def clear_sections(self) -> None:
        pass

    def reset(self) -> None:
        pass
