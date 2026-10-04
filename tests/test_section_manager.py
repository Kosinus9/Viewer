import unittest
from contextlib import nullcontext
from unittest.mock import Mock, patch

from src.backend.application.CLS_LayoutManager import CLS_LayoutManager
from src.backend.application.CLS_SectionManager import CLS_SectionManager
from src.backend.domain.CLS_ViewSection import CLS_ViewSection
from src.backend.domain.DUT.ENUM.E_CommandType import E_CommandType
from src.backend.domain.DUT.ENUM.E_FileType import E_FileType
from src.backend.domain.DUT.ENUM.E_ViewSectionState import E_ViewSectionState
from src.backend.domain.DUT.STRUCT.ST_Job import ST_Job
from src.backend.domain.DUT.STRUCT.ST_JobSection import ST_JobSection
from src.backend.domain.DUT.STRUCT.ST_JobLayout import ST_JobLayout
from src.backend.domain.DUT.STRUCT.ST_JobLifecycle import ST_JobLifecycle


class TestSectionManager(unittest.TestCase):
    def test_layout_identity_is_preserved_from_manager_through_show_to_renderer(self):
        clsLayoutManager = CLS_LayoutManager()
        clsLayoutManager.set_screen_dimensions(1920, 1080)
        clsSectionManager = CLS_SectionManager(clsLayoutManager)
        for index in range(1, 5):
            section_id = str(index)
            clsViewSection = self.create_test_section(clsSectionManager, section_id)
            clsRenderer = clsViewSection._clsRenderer
            with patch.object(clsViewSection, "show", wraps=clsViewSection.show) as show, \
                    patch.object(clsRenderer, "render") as render, \
                    patch.object(clsLayoutManager, "calculate_layouts", wraps=clsLayoutManager.calculate_layouts) as calculate_layouts:
                clsSectionManager.on_section_loaded(section_id)
                calculate_layouts.assert_called_once_with(index)
                stJobLayout = clsSectionManager._stJobLayouts[section_id]
                show.assert_called_once_with(stJobLayout)
                render.assert_called_once_with(stJobLayout)
                self.assertIs(show.call_args.args[0], stJobLayout)
                self.assertIs(render.call_args.args[0], stJobLayout)
                self.assertIs(clsViewSection._clsRenderer, clsRenderer)

    def test_on_section_loaded_requests_show_when_space_available(self):
        for number_of_active_section in range(4):
            with self.subTest(number_of_active_section=number_of_active_section):
                clsSectionManager = CLS_SectionManager(Mock(spec=CLS_LayoutManager))
                for index in range(number_of_active_section):
                    clsVisibleViewSection = CLS_ViewSection(str(index), "visible.pdf", "visible.pdf")
                    clsVisibleViewSection.visible()
                    clsSectionManager.view_sections[str(index)] = clsVisibleViewSection
                clsViewSection = CLS_ViewSection("loading", "resource.pdf", "resource.pdf")
                with patch("src.backend.infrastructure.renderers.CLS_PDFRenderer.CLS_PDFRenderer.load", return_value=True):
                    clsViewSection.initialize()
                clsSectionManager.view_sections["loading"] = clsViewSection
                with patch.object(clsSectionManager, "show_section") as show_section, \
                        patch.object(clsViewSection, "background") as background:
                    clsSectionManager.on_section_loaded("loading")
                    show_section.assert_called_once_with("loading")
                    background.assert_not_called()
                self.assertIs(clsViewSection.state, E_ViewSectionState.LOADING)

    def test_on_section_loaded_backgrounds_section_when_four_visible(self):
        clsSectionManager = CLS_SectionManager(Mock(spec=CLS_LayoutManager))
        for index in range(4):
            clsVisibleViewSection = CLS_ViewSection(str(index), "visible.pdf", "visible.pdf")
            clsVisibleViewSection.visible()
            clsSectionManager.view_sections[str(index)] = clsVisibleViewSection
        clsViewSection = CLS_ViewSection("loading", "resource.pdf", "resource.pdf")
        with patch("src.backend.infrastructure.renderers.CLS_PDFRenderer.CLS_PDFRenderer.load", return_value=True):
            clsViewSection.initialize()
        clsSectionManager.view_sections["loading"] = clsViewSection
        with patch.object(clsSectionManager, "show_section") as show_section, \
                patch.object(clsViewSection, "background", wraps=clsViewSection.background) as background:
            clsSectionManager.on_section_loaded("loading")
            show_section.assert_not_called()
            background.assert_called_once_with()
        self.assertIs(clsViewSection.state, E_ViewSectionState.BACKGROUND)

    def test_on_section_loaded_ignores_missing_and_nonloading_sections(self):
        clsSectionManager = CLS_SectionManager(Mock(spec=CLS_LayoutManager))
        clsViewSection = CLS_ViewSection("section", "resource.pdf", "resource.pdf")
        clsSectionManager.view_sections["section"] = clsViewSection
        with patch.object(clsSectionManager, "show_section") as show_section, \
                patch.object(clsViewSection, "background") as background:
            clsSectionManager.on_section_loaded("missing")
            for state in (None, E_ViewSectionState.VISIBLE, E_ViewSectionState.ERROR, E_ViewSectionState.CLOSING, E_ViewSectionState.CLOSED):
                if state is not None:
                    getattr(clsViewSection, state.value)()
                clsSectionManager.on_section_loaded("section")
            show_section.assert_not_called()
            background.assert_not_called()

    def test_open_success_automatically_shows_four_sections_and_backgrounds_fifth(self):
        clsLayoutManager = CLS_LayoutManager()
        clsLayoutManager.set_screen_dimensions(1920, 1080)
        clsSectionManager = CLS_SectionManager(clsLayoutManager)
        for index in range(1, 6):
            with patch.object(clsLayoutManager, "calculate_layouts", wraps=clsLayoutManager.calculate_layouts) as calculate_layouts:
                clsViewSection = self.create_test_section(clsSectionManager, str(index), complete_loading=True)
                if index <= 4:
                    self.assertIs(clsViewSection.state, E_ViewSectionState.VISIBLE)
                    calculate_layouts.assert_called_once_with(index)
                    self.assertEqual(list(clsSectionManager._stJobLayouts), [str(number) for number in range(1, index + 1)])
                    self.assertEqual(list(clsSectionManager._stJobLayouts.values()), clsLayoutManager.calculate_layouts(index))
                else:
                    self.assertIs(clsViewSection.state, E_ViewSectionState.BACKGROUND)
                    self.assertNotIn("5", clsSectionManager._stJobLayouts)
                    calculate_layouts.assert_not_called()
        self.assertEqual(len(clsSectionManager.view_sections), 5)

    def test_explicit_loading_event_recomputes_target_layout_and_limits_visibility(self):
        clsLayoutManager = CLS_LayoutManager()
        clsLayoutManager.set_screen_dimensions(1920, 1080)
        clsSectionManager = CLS_SectionManager(clsLayoutManager)
        for index in range(1, 6):
            section_id = str(index)
            clsViewSection = self.create_test_section(clsSectionManager, section_id)
            self.assertIs(clsViewSection.state, E_ViewSectionState.LOADING)
            self.assertNotIn(section_id, clsSectionManager._stJobLayouts)
            with patch.object(clsLayoutManager, "calculate_layouts", wraps=clsLayoutManager.calculate_layouts) as calculate_layouts:
                clsSectionManager.on_section_loaded(section_id)
                if index <= 4:
                    calculate_layouts.assert_called_once_with(index)
                    self.assertIs(clsViewSection.state, E_ViewSectionState.VISIBLE)
                    self.assertEqual(list(clsSectionManager._stJobLayouts), [str(number) for number in range(1, index + 1)])
                    self.assertEqual(list(clsSectionManager._stJobLayouts.values()), clsLayoutManager.calculate_layouts(index))
                else:
                    calculate_layouts.assert_not_called()
                    self.assertIs(clsViewSection.state, E_ViewSectionState.BACKGROUND)
                    self.assertNotIn(section_id, clsSectionManager._stJobLayouts)
        with patch.object(clsLayoutManager, "calculate_layouts", wraps=clsLayoutManager.calculate_layouts) as calculate_layouts:
            clsSectionManager.on_section_loaded("1")
            clsSectionManager.on_section_loaded("5")
            clsSectionManager.on_section_loaded("missing")
            calculate_layouts.assert_not_called()

    def test_failed_loading_event_cannot_make_error_section_visible(self):
        clsLayoutManager = Mock(spec=CLS_LayoutManager)
        clsSectionManager = CLS_SectionManager(clsLayoutManager)
        stJob = ST_Job(
            command_type=E_CommandType.OPEN,
            stJobSection=ST_JobSection("invalid.xyz", "invalid.xyz", "error"),
            stJobLayout=ST_JobLayout(0, 0, 0, 0),
            stJobLifecycle=ST_JobLifecycle(),
        )
        clsSectionManager.create_section(stJob)
        clsSectionManager.on_section_loaded("error")
        self.assertIs(clsSectionManager.get_section("error").state, E_ViewSectionState.ERROR)
        self.assertEqual(clsSectionManager._stJobLayouts, {})
        clsLayoutManager.calculate_layouts.assert_not_called()

    def test_maps_one_to_four_sections_in_registry_order(self):
        clsLayoutManager = CLS_LayoutManager()
        clsLayoutManager.set_screen_dimensions(1920, 1080)
        clsSectionManager = CLS_SectionManager(clsLayoutManager)
        section_ids = ["z", "a", "q", "b"]
        for index, section_id in enumerate(section_ids, start=1):
            clsViewSection = self.create_test_section(clsSectionManager, section_id)
            clsViewSection.background()
            previous_layouts = dict(clsSectionManager._stJobLayouts)
            with patch.object(clsLayoutManager, "calculate_layouts", wraps=clsLayoutManager.calculate_layouts) as calculate_layouts:
                clsSectionManager.show_section(section_id)
                calculate_layouts.assert_called_once_with(index)
            self.assertEqual(list(clsSectionManager._stJobLayouts), section_ids[:index])
            self.assertEqual(list(clsSectionManager._stJobLayouts.values()), clsLayoutManager.calculate_layouts(index))
            for previous_id, stPreviousJobLayout in previous_layouts.items():
                self.assertIsNot(clsSectionManager._stJobLayouts[previous_id], stPreviousJobLayout)

    def test_hide_close_and_reshow_replace_obsolete_associations(self):
        clsLayoutManager = CLS_LayoutManager()
        clsLayoutManager.set_screen_dimensions(1920, 1080)
        clsSectionManager = CLS_SectionManager(clsLayoutManager)
        for section_id in ("first", "second", "third"):
            clsViewSection = self.create_test_section(clsSectionManager, section_id)
            clsViewSection.background()
            clsSectionManager.show_section(section_id)
        clsSectionManager.hide_section("second")
        self.assertEqual(list(clsSectionManager._stJobLayouts), ["first", "third"])
        self.assertEqual(list(clsSectionManager._stJobLayouts.values()), clsLayoutManager.calculate_layouts(2))
        clsSectionManager.show_section("second")
        self.assertEqual(list(clsSectionManager._stJobLayouts), ["first", "second", "third"])
        clsSectionManager.close_section("first")
        self.assertIsNone(clsSectionManager.get_section("first"))
        self.assertEqual(list(clsSectionManager._stJobLayouts), ["second", "third"])
        self.assertEqual(list(clsSectionManager._stJobLayouts.values()), clsLayoutManager.calculate_layouts(2))
        clsSectionManager.hide_section("second")
        clsSectionManager.close_section("third")
        self.assertEqual(clsSectionManager._stJobLayouts, {})

    def test_fifth_section_stays_background_until_explicit_show_after_space_freed(self):
        clsLayoutManager = CLS_LayoutManager()
        clsLayoutManager.set_screen_dimensions(1920, 1080)
        clsSectionManager = CLS_SectionManager(clsLayoutManager)
        for section_id in ("1", "2", "3", "4", "5"):
            clsViewSection = self.create_test_section(clsSectionManager, section_id)
            clsViewSection.background()
            clsSectionManager.show_section(section_id)
        self.assertIs(clsSectionManager.get_section("5").state, E_ViewSectionState.BACKGROUND)
        self.assertEqual(list(clsSectionManager._stJobLayouts), ["1", "2", "3", "4"])
        previous_layouts = dict(clsSectionManager._stJobLayouts)
        with patch.object(clsLayoutManager, "calculate_layouts", wraps=clsLayoutManager.calculate_layouts) as calculate_layouts:
            clsSectionManager.show_section("5")
            clsSectionManager.show_section("1")
            calculate_layouts.assert_not_called()
        self.assertEqual(clsSectionManager._stJobLayouts, previous_layouts)
        clsSectionManager.hide_section("2")
        clsSectionManager.show_section("5")
        self.assertEqual(list(clsSectionManager._stJobLayouts), ["1", "3", "4", "5"])
        self.assertIs(clsSectionManager.get_section("5").state, E_ViewSectionState.VISIBLE)

    def test_missing_dimensions_clear_old_mapping_without_changing_visibility(self):
        clsLayoutManager = CLS_LayoutManager()
        clsSectionManager = CLS_SectionManager(clsLayoutManager)
        clsViewSection = self.create_test_section(clsSectionManager, "section")
        clsViewSection.background()
        clsSectionManager.show_section("section")
        self.assertEqual(clsSectionManager._stJobLayouts, {})
        self.assertEqual(clsSectionManager.update_layout(), [])
        self.assertIs(clsViewSection.state, E_ViewSectionState.BACKGROUND)
        clsLayoutManager.set_screen_dimensions(800, 600)
        clsSectionManager.show_section("section")
        self.assertEqual(clsSectionManager._stJobLayouts, {"section": ST_JobLayout(200, 150, 400, 300)})
        clsSectionManager.clear_sections()
        self.assertEqual(clsSectionManager._stJobLayouts, {})

    def create_test_section(self, clsSectionManager, section_id, complete_loading=False):
        stJob = ST_Job(
            command_type=E_CommandType.OPEN,
            stJobSection=ST_JobSection(section_id + ".pdf", "documents/" + section_id + ".pdf", section_id),
            stJobLayout=ST_JobLayout(0, 0, 0, 0),
            stJobLifecycle=ST_JobLifecycle(),
        )
        # State-specific tests prepare sections before the completion event.
        completion_context = nullcontext() if complete_loading else patch.object(clsSectionManager, "on_section_loaded")
        with completion_context, patch("src.backend.infrastructure.renderers.CLS_PDFRenderer.CLS_PDFRenderer.load", return_value=True):
            clsSectionManager.create_section(stJob)
        return clsSectionManager.get_section(section_id)

    def test_no_visible_sections_returns_empty_layout_without_calculation(self):
        clsLayoutManager = Mock(spec=CLS_LayoutManager)
        clsSectionManager = CLS_SectionManager(clsLayoutManager)
        self.assertEqual(clsSectionManager.get_number_of_active_section(), 0)
        self.assertEqual(clsSectionManager.update_layout(), [])
        clsLayoutManager.calculate_layouts.assert_not_called()

    def test_only_visible_sections_are_counted(self):
        clsLayoutManager = Mock(spec=CLS_LayoutManager)
        clsSectionManager = CLS_SectionManager(clsLayoutManager)
        for state in E_ViewSectionState:
            clsViewSection = self.create_test_section(clsSectionManager, state.value)
            if state != E_ViewSectionState.LOADING:
                getattr(clsViewSection, state.value)()
        clsViewSection = CLS_ViewSection("uninitialized", "resource", "resource")
        clsSectionManager.view_sections[clsViewSection.section_id] = clsViewSection
        self.assertEqual(clsSectionManager.get_number_of_active_section(), 1)
        self.assertEqual(len(clsSectionManager.view_sections), 7)
        clsLayoutManager.calculate_layouts.assert_not_called()

    def test_update_layout_passes_one_to_four_visible_sections_and_returns_result(self):
        clsLayoutManager = CLS_LayoutManager()
        clsLayoutManager.set_screen_dimensions(1920, 1080)
        clsSectionManager = CLS_SectionManager(clsLayoutManager)
        for number_of_active_section in range(1, 5):
            clsViewSection = self.create_test_section(clsSectionManager, str(number_of_active_section))
            clsViewSection.visible()
            self.assertEqual(clsSectionManager.get_number_of_active_section(), number_of_active_section)
            with patch.object(clsLayoutManager, "calculate_layouts", wraps=clsLayoutManager.calculate_layouts) as calculate_layouts:
                stJobLayouts = clsSectionManager.update_layout()
                calculate_layouts.assert_called_once_with(number_of_active_section)
            self.assertEqual(len(stJobLayouts), number_of_active_section)
            self.assertTrue(all(isinstance(stJobLayout, ST_JobLayout) for stJobLayout in stJobLayouts))
        stJobLayouts = [ST_JobLayout(index, 0, 1, 1) for index in range(4)]
        with patch.object(clsLayoutManager, "calculate_layouts", return_value=stJobLayouts):
            self.assertIs(clsSectionManager.update_layout(), stJobLayouts)

    def test_show_calculates_target_layout_before_state_change(self):
        clsLayoutManager = Mock(spec=CLS_LayoutManager)
        clsSectionManager = CLS_SectionManager(clsLayoutManager)
        clsViewSection = self.create_test_section(clsSectionManager, "section")
        clsViewSection.background()

        def calculate_layouts(number_of_active_section):
            self.assertIs(clsViewSection.state, E_ViewSectionState.BACKGROUND)
            self.assertEqual(number_of_active_section, 1)
            return [ST_JobLayout(0, 0, 960, 540)]

        clsLayoutManager.calculate_layouts.side_effect = calculate_layouts
        clsSectionManager.show_section(clsViewSection.section_id)
        clsLayoutManager.calculate_layouts.assert_called_once_with(1)

    def test_hide_and_close_recalculate_after_state_and_registry_changes(self):
        for action in ("hide_section", "close_section"):
            with self.subTest(action=action):
                clsLayoutManager = Mock(spec=CLS_LayoutManager)
                clsSectionManager = CLS_SectionManager(clsLayoutManager)
                clsViewSection = self.create_test_section(clsSectionManager, "target")
                clsOtherViewSection = self.create_test_section(clsSectionManager, "other")
                clsViewSection.visible()
                clsOtherViewSection.visible()

                def calculate_layouts(number_of_active_section):
                    self.assertEqual(number_of_active_section, 1)
                    self.assertIs(clsOtherViewSection.state, E_ViewSectionState.VISIBLE)
                    if action == "hide_section":
                        self.assertIs(clsViewSection.state, E_ViewSectionState.BACKGROUND)
                        self.assertIs(clsSectionManager.get_section("target"), clsViewSection)
                    else:
                        self.assertIs(clsViewSection.state, E_ViewSectionState.CLOSING)
                        self.assertIsNone(clsSectionManager.get_section("target"))
                    return [ST_JobLayout(0, 0, 960, 540)]

                clsLayoutManager.calculate_layouts.side_effect = calculate_layouts
                getattr(clsSectionManager, action)("target")
                clsLayoutManager.calculate_layouts.assert_called_once_with(1)

    def test_last_visible_section_triggers_update_without_zero_calculation(self):
        for action in ("hide_section", "close_section"):
            with self.subTest(action=action):
                clsLayoutManager = Mock(spec=CLS_LayoutManager)
                clsSectionManager = CLS_SectionManager(clsLayoutManager)
                clsViewSection = self.create_test_section(clsSectionManager, "target")
                clsViewSection.visible()
                with patch.object(clsSectionManager, "update_layout", wraps=clsSectionManager.update_layout) as update_layout:
                    getattr(clsSectionManager, action)("target")
                    update_layout.assert_called_once_with()
                self.assertEqual(clsSectionManager.get_number_of_active_section(), 0)
                clsLayoutManager.calculate_layouts.assert_not_called()

    def test_missing_section_does_not_trigger_recalculation(self):
        clsLayoutManager = Mock(spec=CLS_LayoutManager)
        clsSectionManager = CLS_SectionManager(clsLayoutManager)
        with patch.object(clsSectionManager, "update_layout") as update_layout:
            for action in ("show_section", "hide_section", "close_section"):
                getattr(clsSectionManager, action)("missing")
            update_layout.assert_not_called()

    def test_new_section_is_registered_before_initializing_exactly_once(self):
        clsLayoutManager = CLS_LayoutManager()
        clsLayoutManager.set_screen_dimensions(1920, 1080)
        clsSectionManager = CLS_SectionManager(clsLayoutManager)
        stJob = ST_Job(
            command_type=E_CommandType.OPEN,
            stJobSection=ST_JobSection(
                file_name="example.pdf",
                file_path="documents/example.pdf",
                section_id="section-from-job",
            ),
            stJobLayout=ST_JobLayout(0, 0, 960, 540),
            stJobLifecycle=ST_JobLifecycle(),
        )

        initialize_section = CLS_ViewSection.initialize

        def check_registration(clsViewSection):
            self.assertIsInstance(clsViewSection, CLS_ViewSection)
            self.assertIs(
                clsSectionManager.view_sections[stJob.stJobSection.section_id],
                clsViewSection,
            )
            initialize_section(clsViewSection)

        with patch.object(CLS_ViewSection, "initialize", autospec=True, side_effect=check_registration) as initialize, \
                patch("src.backend.infrastructure.renderers.CLS_PDFRenderer.CLS_PDFRenderer.load", return_value=True):
            section_id = clsSectionManager.create_section(stJob)
            clsViewSection = clsSectionManager.get_section(section_id)
            initialize.assert_called_once_with(clsViewSection)

        self.assertEqual(section_id, stJob.stJobSection.section_id)
        self.assertEqual(len(clsSectionManager.view_sections), 1)
        self.assertEqual(clsViewSection.section_id, section_id)
        self.assertEqual(clsViewSection.file_name, stJob.stJobSection.file_name)
        self.assertEqual(clsViewSection.file_path, stJob.stJobSection.file_path)
        self.assertIs(clsViewSection.file_type, E_FileType.PDF)
        self.assertIs(clsViewSection.state, E_ViewSectionState.VISIBLE)
        self.assertEqual(clsSectionManager._stJobLayouts, {section_id: ST_JobLayout(480, 270, 960, 540)})


if __name__ == "__main__":
    unittest.main()
