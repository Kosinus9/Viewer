import unittest
from unittest.mock import patch

from src.backend.domain.CLS_ViewSection import CLS_ViewSection
from src.backend.domain.DUT.ENUM.E_FileType import E_FileType
from src.backend.domain.DUT.ENUM.E_ViewSectionState import E_ViewSectionState
from src.backend.infrastructure.CLS_PDFRenderer import CLS_PDFRenderer
from src.backend.infrastructure.CLS_ImageRenderer import CLS_ImageRenderer
from src.backend.infrastructure.CLS_VideoRenderer import CLS_VideoRenderer
from src.backend.infrastructure.CLS_TextRenderer import CLS_TextRenderer


class TestViewSection(unittest.TestCase):
    def test_file_type_is_undetermined_before_initialization(self):
        clsViewSection = CLS_ViewSection("section-1", "document.pdf", "documents/document.pdf")
        self.assertIsNone(clsViewSection.file_type)
        self.assertIsNone(clsViewSection.state)
        self.assertIsNone(clsViewSection._clsRenderer)

    def test_initialize_selects_and_retains_renderer_for_each_family(self):
        for extensions, expected_type, renderer_class in (
            ((".pdf",), E_FileType.PDF, CLS_PDFRenderer),
            ((".jpg", ".jpeg", ".png", ".bmp", ".webp"), E_FileType.IMAGE, CLS_ImageRenderer),
            ((".mp4", ".avi", ".mkv", ".mov", ".webm"), E_FileType.VIDEO, CLS_VideoRenderer),
            ((".txt", ".text"), E_FileType.TEXT, CLS_TextRenderer),
        ):
            for extension in extensions:
                for suffix in (extension, extension.upper()):
                    with self.subTest(extension=suffix):
                        file_path = "documents/resource" + suffix
                        clsViewSection = CLS_ViewSection("section-1", "original-name.bin", file_path)
                        clsViewSection.initialize()
                        self.assertIs(clsViewSection.file_type, expected_type)
                        self.assertIsInstance(clsViewSection._clsRenderer, renderer_class)
                        self.assertIs(clsViewSection.state, E_ViewSectionState.LOADING)
                        self.assertEqual(clsViewSection.file_name, "original-name.bin")
                        self.assertEqual(clsViewSection.file_path, file_path)

    def test_unknown_extension_has_no_renderer(self):
        for file_path in ("documents/resource", "documents/resource.xyz"):
            with self.subTest(file_path=file_path):
                clsViewSection = CLS_ViewSection("section-1", "resource", file_path)
                clsViewSection.initialize()
                self.assertIs(clsViewSection.file_type, E_FileType.UNKNOWN)
                self.assertIsNone(clsViewSection._clsRenderer)
                self.assertIs(clsViewSection.state, E_ViewSectionState.ERROR)

    def test_initialize_identifies_type_from_file_path(self):
        for file_path, expected_type in (
            ("documents/document.pdf", E_FileType.PDF),
            ("documents/document.PDF", E_FileType.PDF),
            ("documents/document", E_FileType.UNKNOWN),
            ("documents/document.txt", E_FileType.TEXT),
            ("documents/document.xyz", E_FileType.UNKNOWN),
        ):
            with self.subTest(file_path=file_path):
                clsViewSection = CLS_ViewSection("section-1", "different-name.bin", file_path)
                clsViewSection.initialize()
                self.assertIs(clsViewSection.file_type, expected_type)
                self.assertIs(
                    clsViewSection.state,
                    E_ViewSectionState.LOADING if expected_type != E_FileType.UNKNOWN
                    else E_ViewSectionState.ERROR,
                )

    def test_defined_transitions(self):
        for initial_state, method_name, expected_state in (
            (E_ViewSectionState.BACKGROUND, "show", E_ViewSectionState.VISIBLE),
            (E_ViewSectionState.VISIBLE, "hide", E_ViewSectionState.BACKGROUND),
            (E_ViewSectionState.VISIBLE, "close", E_ViewSectionState.CLOSING),
            (E_ViewSectionState.BACKGROUND, "close", E_ViewSectionState.CLOSING),
            (E_ViewSectionState.ERROR, "close", E_ViewSectionState.CLOSING),
        ):
            with self.subTest(initial_state=initial_state, method=method_name):
                clsViewSection = CLS_ViewSection("section-1", "document.pdf", "documents/document.pdf")
                with patch.object(clsViewSection, "_state", initial_state):
                    getattr(clsViewSection, method_name)()
                    self.assertIs(clsViewSection.state, expected_state)

    def test_actions_call_state_methods(self):
        for initial_state, action, state_method in (
            (None, "initialize", "loading"),
            (E_ViewSectionState.BACKGROUND, "show", "visible"),
            (E_ViewSectionState.VISIBLE, "hide", "background"),
            (E_ViewSectionState.VISIBLE, "close", "closing"),
            (E_ViewSectionState.BACKGROUND, "close", "closing"),
            (E_ViewSectionState.ERROR, "close", "closing"),
        ):
            with self.subTest(action=action, initial_state=initial_state):
                clsViewSection = CLS_ViewSection("section-1", "document.pdf", "documents/document.pdf")
                with patch.object(clsViewSection, "_state", initial_state), \
                        patch.object(clsViewSection, state_method) as enter_state, \
                        patch.object(clsViewSection, "closed") as closed:
                    getattr(clsViewSection, action)()
                    enter_state.assert_called_once_with()
                    closed.assert_not_called()
                    self.assertIs(clsViewSection.state, initial_state)

    def test_initialize_unsupported_file_calls_error(self):
        clsViewSection = CLS_ViewSection("section-1", "document.xyz", "documents/document.xyz")
        with patch.object(clsViewSection, "error") as error:
            clsViewSection.initialize()
            error.assert_called_once_with()
        self.assertIs(clsViewSection.file_type, E_FileType.UNKNOWN)
        self.assertIsNone(clsViewSection.state)

    def test_state_methods_enter_corresponding_states(self):
        clsViewSection = CLS_ViewSection("section-1", "document.pdf", "documents/document.pdf")
        for state in E_ViewSectionState:
            with self.subTest(state=state):
                getattr(clsViewSection, state.value)()
                self.assertIs(clsViewSection.state, state)

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
            clsViewSection.file_type = E_FileType.UNKNOWN
        self.assertIs(clsViewSection.file_type, E_FileType.PDF)


if __name__ == "__main__":
    unittest.main()
