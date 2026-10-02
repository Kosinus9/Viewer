import unittest
from unittest.mock import patch

from src.backend.domain.CLS_ViewSection import CLS_ViewSection
from src.backend.domain.DUT.ENUM.E_FileType import E_FileType
from src.backend.domain.DUT.ENUM.E_ViewSectionState import E_ViewSectionState


class TestViewSection(unittest.TestCase):
    def test_file_type_is_undetermined_before_initialization(self):
        clsViewSection = CLS_ViewSection("section-1", "document.pdf", "documents/document.pdf")
        self.assertIsNone(clsViewSection.file_type)
        self.assertIsNone(clsViewSection.state)

    def test_initialize_identifies_type_from_file_path(self):
        for file_path, expected_type in (
            ("documents/document.pdf", E_FileType.PDF),
            ("documents/document.PDF", E_FileType.PDF),
            ("documents/document", E_FileType.ERROR),
            ("documents/document.txt", E_FileType.ERROR),
            ("documents/document.xyz", E_FileType.ERROR),
        ):
            with self.subTest(file_path=file_path):
                clsViewSection = CLS_ViewSection("section-1", "different-name.bin", file_path)
                clsViewSection.initialize()
                self.assertIs(clsViewSection.file_type, expected_type)
                self.assertIs(
                    clsViewSection.state,
                    E_ViewSectionState.LOADING if expected_type == E_FileType.PDF
                    else E_ViewSectionState.ERROR,
                )

    def test_defined_transitions(self):
        for initial_state, method_name, expected_state in (
            (E_ViewSectionState.BACKGROUND, "show", E_ViewSectionState.VISIBLE),
            (E_ViewSectionState.VISIBLE, "hide", E_ViewSectionState.BACKGROUND),
            (E_ViewSectionState.VISIBLE, "close", E_ViewSectionState.CLOSED),
            (E_ViewSectionState.BACKGROUND, "close", E_ViewSectionState.CLOSED),
            (E_ViewSectionState.ERROR, "close", E_ViewSectionState.CLOSED),
        ):
            with self.subTest(initial_state=initial_state, method=method_name):
                clsViewSection = CLS_ViewSection("section-1", "document.pdf", "documents/document.pdf")
                with patch.object(clsViewSection, "_state", initial_state):
                    getattr(clsViewSection, method_name)()
                    self.assertIs(clsViewSection.state, expected_state)

    def test_undefined_transitions_preserve_state(self):
        allowed_states = {
            "show": {E_ViewSectionState.BACKGROUND},
            "hide": {E_ViewSectionState.VISIBLE},
            "close": {E_ViewSectionState.VISIBLE, E_ViewSectionState.BACKGROUND, E_ViewSectionState.ERROR},
        }
        for method_name, states in allowed_states.items():
            for initial_state in (None, *E_ViewSectionState):
                if initial_state in states:
                    continue
                with self.subTest(method=method_name, initial_state=initial_state):
                    clsViewSection = CLS_ViewSection("section-1", "document.pdf", "documents/document.pdf")
                    with patch.object(clsViewSection, "_state", initial_state):
                        getattr(clsViewSection, method_name)()
                        self.assertIs(clsViewSection.state, initial_state)

    def test_state_is_read_only(self):
        clsViewSection = CLS_ViewSection("section-1", "document.pdf", "documents/document.pdf")
        clsViewSection.initialize()
        with self.assertRaises(AttributeError):
            clsViewSection.state = E_ViewSectionState.VISIBLE
        self.assertIs(clsViewSection.state, E_ViewSectionState.LOADING)

    def test_file_type_is_read_only(self):
        clsViewSection = CLS_ViewSection("section-1", "document.pdf", "documents/document.pdf")
        clsViewSection.initialize()
        with self.assertRaises(AttributeError):
            clsViewSection.file_type = E_FileType.ERROR
        self.assertIs(clsViewSection.file_type, E_FileType.PDF)


if __name__ == "__main__":
    unittest.main()
