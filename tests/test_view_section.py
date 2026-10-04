import unittest
from unittest.mock import patch

from src.backend.domain.CLS_ViewSection import CLS_ViewSection
from src.backend.domain.DUT.STRUCT.ST_JobLayout import ST_JobLayout
from src.backend.domain.DUT.ENUM.E_FileType import E_FileType
from src.backend.domain.DUT.ENUM.E_ViewSectionState import E_ViewSectionState
from src.backend.infrastructure.renderers.CLS_PDFRenderer import CLS_PDFRenderer
from src.backend.infrastructure.renderers.CLS_ImageRenderer import CLS_ImageRenderer
from src.backend.infrastructure.renderers.CLS_VideoRenderer import CLS_VideoRenderer
from src.backend.infrastructure.renderers.CLS_TextRenderer import CLS_TextRenderer


class TestViewSection(unittest.TestCase):
    def test_show_calls_layout_transmission_only_for_allowed_transitions(self):
        for initial_state in (None, *E_ViewSectionState):
            with self.subTest(initial_state=initial_state):
                clsViewSection = CLS_ViewSection("section", "resource.pdf", "resource.pdf")
                stJobLayout = ST_JobLayout(480, 270, 960, 540)
                with patch.object(clsViewSection, "_state", initial_state), \
                        patch.object(clsViewSection, "send_layout_to_renderer_for_display") as send_layout:
                    clsViewSection.show(stJobLayout)
                    if initial_state in (E_ViewSectionState.LOADING, E_ViewSectionState.BACKGROUND):
                        send_layout.assert_called_once_with(stJobLayout)
                        self.assertIs(send_layout.call_args.args[0], stJobLayout)
                        self.assertIs(clsViewSection.state, E_ViewSectionState.VISIBLE)
                    else:
                        send_layout.assert_not_called()
                        self.assertIs(clsViewSection.state, initial_state)

    def test_layout_transmission_passes_same_object_to_existing_renderer(self):
        clsViewSection = CLS_ViewSection("section", "resource.pdf", "resource.pdf")
        clsViewSection.initialize()
        clsRenderer = clsViewSection._clsRenderer
        stJobLayout = ST_JobLayout(480, 270, 960, 540)
        with patch.object(clsRenderer, "render") as render:
            clsViewSection.send_layout_to_renderer_for_display(stJobLayout)
            render.assert_called_once_with(stJobLayout)
            self.assertIs(render.call_args.args[0], stJobLayout)
        self.assertIs(clsViewSection._clsRenderer, clsRenderer)
        self.assertIs(clsViewSection.state, E_ViewSectionState.LOADING)

    def test_show_passes_same_layout_to_existing_renderer_for_each_family(self):
        for suffix in (".pdf", ".png", ".mp4", ".txt"):
            for initial_state in (E_ViewSectionState.LOADING, E_ViewSectionState.BACKGROUND):
                with self.subTest(suffix=suffix, initial_state=initial_state):
                    clsViewSection = CLS_ViewSection("section", "resource" + suffix, "resource" + suffix)
                    clsViewSection.initialize()
                    if initial_state == E_ViewSectionState.BACKGROUND:
                        clsViewSection.background()
                    clsRenderer = clsViewSection._clsRenderer
                    stJobLayout = ST_JobLayout(480, 270, 960, 540)
                    with patch.object(clsRenderer, "render") as render:
                        clsViewSection.show(stJobLayout)
                        render.assert_called_once_with(stJobLayout)
                        self.assertIs(render.call_args.args[0], stJobLayout)
                        self.assertIs(clsViewSection.state, E_ViewSectionState.VISIBLE)
                        clsViewSection.show(stJobLayout)
                        render.assert_called_once_with(stJobLayout)
                    self.assertIs(clsViewSection._clsRenderer, clsRenderer)

    def test_show_does_not_render_from_unauthorized_states(self):
        clsViewSection = CLS_ViewSection("section", "resource.pdf", "resource.pdf")
        clsViewSection.initialize()
        with patch.object(clsViewSection._clsRenderer, "render") as render:
            for state in (E_ViewSectionState.ERROR, E_ViewSectionState.CLOSING, E_ViewSectionState.CLOSED):
                getattr(clsViewSection, state.value)()
                clsViewSection.show(ST_JobLayout(0, 0, 960, 540))
                self.assertIs(clsViewSection.state, state)
            render.assert_not_called()

    def setUp(self):
        for renderer_class in (CLS_PDFRenderer, CLS_ImageRenderer, CLS_VideoRenderer, CLS_TextRenderer):
            patcher = patch.object(renderer_class, "load", return_value=True)
            patcher.start()
            self.addCleanup(patcher.stop)

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
            (E_ViewSectionState.LOADING, "show", E_ViewSectionState.VISIBLE),
            (E_ViewSectionState.BACKGROUND, "show", E_ViewSectionState.VISIBLE),
            (E_ViewSectionState.VISIBLE, "hide", E_ViewSectionState.BACKGROUND),
            (E_ViewSectionState.VISIBLE, "close", E_ViewSectionState.CLOSING),
            (E_ViewSectionState.BACKGROUND, "close", E_ViewSectionState.CLOSING),
            (E_ViewSectionState.ERROR, "close", E_ViewSectionState.CLOSING),
        ):
            with self.subTest(initial_state=initial_state, method=method_name):
                clsViewSection = CLS_ViewSection("section-1", "document.pdf", "documents/document.pdf")
                with patch.object(clsViewSection, "_state", initial_state):
                    getattr(clsViewSection, method_name)(*([ST_JobLayout(0, 0, 960, 540)] if method_name == "show" else []))
                    self.assertIs(clsViewSection.state, expected_state)

    def test_show_after_loading_enters_visible_without_background(self):
        clsViewSection = CLS_ViewSection("section-1", "document.pdf", "documents/document.pdf")
        clsViewSection.initialize()
        self.assertIs(clsViewSection.state, E_ViewSectionState.LOADING)
        with patch.object(clsViewSection, "background") as background, \
                patch.object(clsViewSection, "visible", wraps=clsViewSection.visible) as visible:
            clsViewSection.show(ST_JobLayout(0, 0, 960, 540))
            visible.assert_called_once_with()
            background.assert_not_called()
        self.assertIs(clsViewSection.state, E_ViewSectionState.VISIBLE)

    def test_show_already_visible_does_not_reenter_visible(self):
        clsViewSection = CLS_ViewSection("section-1", "document.pdf", "documents/document.pdf")
        clsViewSection.visible()
        with patch.object(clsViewSection, "visible") as visible:
            clsViewSection.show(ST_JobLayout(0, 0, 960, 540))
            visible.assert_not_called()
        self.assertIs(clsViewSection.state, E_ViewSectionState.VISIBLE)

    def test_actions_call_state_methods(self):
        for initial_state, action, state_method in (
            (E_ViewSectionState.LOADING, "show", "visible"),
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
                    getattr(clsViewSection, action)(*([ST_JobLayout(0, 0, 960, 540)] if action == "show" else []))
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
        clsViewSection.initialize()
        for state in E_ViewSectionState:
            with self.subTest(state=state):
                getattr(clsViewSection, state.value)()
                self.assertIs(clsViewSection.state, state)

    def test_loading_delegates_once_to_selected_renderer_while_loading(self):
        self.doCleanups()
        for suffix, renderer_class in (
            (".pdf", CLS_PDFRenderer), (".png", CLS_ImageRenderer),
            (".mp4", CLS_VideoRenderer), (".txt", CLS_TextRenderer),
        ):
            for loading_success in (True, False):
                with self.subTest(suffix=suffix, loading_success=loading_success):
                    file_path = "documents/resource" + suffix
                    clsViewSection = CLS_ViewSection("section-1", "original-name", file_path)

                    def observe_load(clsRenderer, received_path):
                        self.assertIs(clsViewSection.state, E_ViewSectionState.LOADING)
                        self.assertIs(clsViewSection._clsRenderer, clsRenderer)
                        self.assertEqual(received_path, file_path)
                        return loading_success

                    with patch.object(renderer_class, "load", autospec=True, side_effect=observe_load) as load:
                        clsViewSection.initialize()
                        load.assert_called_once_with(clsViewSection._clsRenderer, file_path)
                    expected_state = E_ViewSectionState.LOADING if loading_success else E_ViewSectionState.ERROR
                    self.assertIs(clsViewSection.state, expected_state)

    def test_loading_without_renderer_enters_error(self):
        clsViewSection = CLS_ViewSection("section-1", "document.pdf", "documents/document.pdf")
        clsViewSection.loading()
        self.assertIs(clsViewSection.state, E_ViewSectionState.ERROR)

    def test_unknown_format_does_not_load_any_renderer(self):
        clsViewSection = CLS_ViewSection("section-1", "document.xyz", "documents/document.xyz")
        clsViewSection.initialize()
        for renderer_class in (CLS_PDFRenderer, CLS_ImageRenderer, CLS_VideoRenderer, CLS_TextRenderer):
            renderer_class.load.assert_not_called()
        self.assertIs(clsViewSection.state, E_ViewSectionState.ERROR)

    def test_undefined_transitions_preserve_state(self):
        allowed_states = {
            "show": {E_ViewSectionState.LOADING, E_ViewSectionState.BACKGROUND},
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
                        getattr(clsViewSection, method_name)(*([ST_JobLayout(0, 0, 960, 540)] if method_name == "show" else []))
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
