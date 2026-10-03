import unittest
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
    def create_test_section(self, clsSectionManager, section_id):
        stJob = ST_Job(
            command_type=E_CommandType.OPEN,
            stJobSection=ST_JobSection(section_id + ".pdf", "documents/" + section_id + ".pdf", section_id),
            stJobLayout=ST_JobLayout(0, 0, 0, 0),
            stJobLifecycle=ST_JobLifecycle(),
        )
        with patch("src.backend.infrastructure.renderers.CLS_PDFRenderer.CLS_PDFRenderer.load", return_value=True):
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
        stJobLayouts = [ST_JobLayout(0, 0, 1, 1)]
        with patch.object(clsLayoutManager, "calculate_layouts", return_value=stJobLayouts):
            self.assertIs(clsSectionManager.update_layout(), stJobLayouts)

    def test_show_recalculates_after_state_change(self):
        clsLayoutManager = Mock(spec=CLS_LayoutManager)
        clsSectionManager = CLS_SectionManager(clsLayoutManager)
        clsViewSection = self.create_test_section(clsSectionManager, "section")
        clsViewSection.background()

        def calculate_layouts(number_of_active_section):
            self.assertIs(clsViewSection.state, E_ViewSectionState.VISIBLE)
            self.assertEqual(number_of_active_section, 1)
            return []

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
                    return []

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
        clsSectionManager = CLS_SectionManager(CLS_LayoutManager())
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
        self.assertIs(clsViewSection.state, E_ViewSectionState.LOADING)


if __name__ == "__main__":
    unittest.main()
