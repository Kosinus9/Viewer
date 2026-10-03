import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from src.backend.application.CLS_CommandManager import CLS_CommandManager
from src.backend.application.CLS_SectionManager import CLS_SectionManager
from src.backend.application.CLS_TimerLifecycleManager import CLS_TimerLifecycleManager
from src.backend.application.CLS_ViewerController import CLS_ViewerController
from src.backend.domain.CLS_ViewSection import CLS_ViewSection
from src.backend.domain.DUT.ENUM.E_CommandType import E_CommandType
from src.backend.domain.DUT.ENUM.E_FileType import E_FileType
from src.backend.domain.DUT.ENUM.E_ViewSectionState import E_ViewSectionState
from src.backend.domain.DUT.STRUCT.ST_Command import ST_Command
from src.backend.infrastructure.renderers.CLS_PDFRenderer import CLS_PDFRenderer
from src.backend.infrastructure.renderers.CLS_TextRenderer import CLS_TextRenderer


class TestOpenFlowIntegration(unittest.TestCase):
    def test_three_sections_initialize_and_route_independently(self):
        clsCommandManager = CLS_CommandManager()
        clsSectionManager = CLS_SectionManager()
        clsTimerLifecycleManager = CLS_TimerLifecycleManager()
        clsViewerController = CLS_ViewerController(
            clsSectionManager, clsTimerLifecycleManager
        )
        sections = {}
        renderers = {}
        initialize_section = CLS_ViewSection.initialize
        resource_directory = TemporaryDirectory()
        self.addCleanup(resource_directory.cleanup)
        resource_path = Path(resource_directory.name)
        (resource_path / "section_a.pdf").write_bytes(b"%PDF-1.4\n%%EOF\n")
        (resource_path / "section_b.TXT").write_text("Viewer integration test", encoding="utf-8")
        (resource_path / "section_c.xyz").write_bytes(b"unsupported resource")

        def observe_initialize(clsViewSection):
            self.assertIs(clsSectionManager.get_section(clsViewSection.section_id), clsViewSection)
            initialize_section(clsViewSection)

        with patch.object(CLS_ViewSection, "initialize", autospec=True, side_effect=observe_initialize) as initialize:
            for label, file_path, expected_type, renderer_class in (
                ("A", "test_documents/section_a.pdf", E_FileType.PDF, CLS_PDFRenderer),
                ("B", "test_documents/section_b.TXT", E_FileType.TEXT, CLS_TextRenderer),
                ("C", "test_documents/section_c.xyz", E_FileType.UNKNOWN, None),
            ):
                file_path = str(resource_path / Path(file_path).name)
                print(f"[TRACE TEMP][Integration] SECTION {label} OPEN")
                stCommand = clsCommandManager.create_open_command(file_path)
                clsViewerController.process_command(stCommand)
                section_id = clsSectionManager.find_section(stCommand.file_name, stCommand.file_path)
                self.assertIsNotNone(section_id)
                self.assertNotIn(section_id, [clsViewSection.section_id for clsViewSection in sections.values()])
                clsViewSection = clsSectionManager.get_section(section_id)
                self.assertIsInstance(clsViewSection, CLS_ViewSection)
                self.assertIs(clsViewSection.file_type, expected_type)
                if renderer_class is None:
                    self.assertIsNone(clsViewSection._clsRenderer)
                    self.assertIs(clsViewSection.state, E_ViewSectionState.ERROR)
                else:
                    self.assertIsInstance(clsViewSection._clsRenderer, renderer_class)
                    self.assertIs(clsViewSection.state, E_ViewSectionState.LOADING)
                sections[label] = clsViewSection
                renderers[label] = clsViewSection._clsRenderer
                self.assertEqual(len(clsSectionManager.view_sections), len(sections))
                for previous_label, clsExistingViewSection in sections.items():
                    self.assertIs(clsSectionManager.get_section(clsExistingViewSection.section_id), clsExistingViewSection)
                    self.assertIs(clsExistingViewSection._clsRenderer, renderers[previous_label])
                    expected_state = E_ViewSectionState.ERROR if previous_label == "C" else E_ViewSectionState.LOADING
                    self.assertIs(clsExistingViewSection.state, expected_state)
            self.assertEqual(initialize.call_count, 3)
            self.assertEqual([entry.args[0] for entry in initialize.call_args_list], list(sections.values()))

        def route(label, command_type):
            clsViewSection = sections[label]
            clsViewerController.process_command(ST_Command(
                command_type, clsViewSection.file_name, clsViewSection.file_path
            ))

        route("A", E_CommandType.SHOW)
        route("B", E_CommandType.HIDE)
        self.assertIs(sections["A"].state, E_ViewSectionState.LOADING)
        self.assertIs(sections["B"].state, E_ViewSectionState.LOADING)
        print("[TRACE TEMP][Integration] Chargement reussi, politique de visibilite absente : preparation manuelle via background() pour A et visible() pour B")
        sections["A"].background()
        sections["B"].visible()
        route("A", E_CommandType.SHOW)
        self.assertIs(sections["A"].state, E_ViewSectionState.VISIBLE)
        self.assertIs(sections["B"].state, E_ViewSectionState.VISIBLE)
        route("B", E_CommandType.HIDE)
        self.assertIs(sections["B"].state, E_ViewSectionState.BACKGROUND)
        self.assertIs(sections["A"].state, E_ViewSectionState.VISIBLE)
        route("C", E_CommandType.SHOW)
        route("C", E_CommandType.HIDE)
        self.assertIs(sections["C"].state, E_ViewSectionState.ERROR)
        self.assertIs(sections["A"].state, E_ViewSectionState.VISIBLE)
        self.assertIs(sections["B"].state, E_ViewSectionState.BACKGROUND)
        self.assertEqual(len({clsViewSection.section_id for clsViewSection in sections.values()}), 3)
        self.assertEqual(len(clsSectionManager.view_sections), 3)
        for label, clsViewSection in sections.items():
            self.assertIs(clsSectionManager.get_section(clsViewSection.section_id), clsViewSection)
            self.assertIs(clsViewSection._clsRenderer, renderers[label])
            renderer_name = type(clsViewSection._clsRenderer).__name__ if clsViewSection._clsRenderer is not None else "None"
            print(
                f"[TRACE TEMP][Integration] SECTION {label} section_id={clsViewSection.section_id} "
                f"file_name={clsViewSection.file_name} file_path={clsViewSection.file_path} "
                f"file_type={clsViewSection.file_type.name} renderer={renderer_name} state={clsViewSection.state.name}"
            )


if __name__ == "__main__":
    unittest.main()
