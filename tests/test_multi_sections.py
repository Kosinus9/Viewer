import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
from uuid import UUID

from src.backend.application.CLS_CommandManager import CLS_CommandManager
from src.backend.application.CLS_SectionManager import CLS_SectionManager
from src.backend.application.CLS_TimerLifecycleManager import CLS_TimerLifecycleManager
from src.backend.application.CLS_ViewerController import CLS_ViewerController
from src.backend.domain.CLS_ViewSection import CLS_ViewSection
from src.backend.domain.DUT.ENUM.E_CommandType import E_CommandType
from src.backend.domain.DUT.STRUCT.ST_Job import ST_Job


class TestMultiSections(unittest.TestCase):
    def test_seven_open_commands_preserve_all_sections(self):
        clsCommandManager = CLS_CommandManager()
        clsSectionManager = CLS_SectionManager()
        clsTimerLifecycleManager = CLS_TimerLifecycleManager()
        clsViewerController = CLS_ViewerController(
            clsSectionManager, clsTimerLifecycleManager
        )
        expected_sections = {}

        with redirect_stdout(io.StringIO()), \
                patch.object(clsViewerController, "create_job", wraps=clsViewerController.create_job) as create_job, \
                patch.object(clsViewerController, "validate_job", wraps=clsViewerController.validate_job) as validate_job, \
                patch.object(clsSectionManager, "create_section", wraps=clsSectionManager.create_section) as create_section:
            for index in range(1, 8):
                with self.subTest(document=index):
                    file_name = f"document_{index:02d}.pdf"
                    file_path = str(Path("test_documents") / file_name)
                    stCommand = clsCommandManager.create_open_command(file_path)
                    self.assertEqual(stCommand.command_type, E_CommandType.OPEN)
                    self.assertIsNone(clsViewerController.process_command(stCommand))

                    self.assertEqual(create_job.call_count, index)
                    self.assertIs(create_job.call_args.args[0], stCommand)
                    self.assertEqual(validate_job.call_count, index)
                    self.assertEqual(create_section.call_count, index)
                    stJob = create_section.call_args.args[0]
                    self.assertIsInstance(stJob, ST_Job)
                    self.assertIs(validate_job.call_args.args[0], stJob)
                    self.assertTrue(CLS_ViewerController.validate_job(clsViewerController, stJob))
                    self.assertEqual(stJob.command_type, E_CommandType.OPEN)
                    section_id = stJob.stJobSection.section_id
                    self.assertIs(type(section_id), str)
                    self.assertTrue(section_id)
                    self.assertEqual(UUID(section_id).version, 4)
                    self.assertNotIn(section_id, expected_sections)

                    clsViewSection = clsSectionManager.get_section(section_id)
                    self.assertIsInstance(clsViewSection, CLS_ViewSection)
                    self.assertEqual(clsViewSection.section_id, section_id)
                    self.assertEqual(clsViewSection.file_name, file_name)
                    self.assertEqual(clsViewSection.file_path, file_path)
                    expected_sections[section_id] = (clsViewSection, file_name, file_path)
                    self.assertEqual(len(clsSectionManager.view_sections), index)
                    self.assertEqual(set(clsSectionManager.view_sections), set(expected_sections))
                    for section_id, (clsViewSection, file_name, file_path) in expected_sections.items():
                        self.assertIs(clsSectionManager.get_section(section_id), clsViewSection)
                        self.assertEqual(clsViewSection.file_name, file_name)
                        self.assertEqual(clsViewSection.file_path, file_path)

        self.assertEqual(len(clsSectionManager.view_sections), 7)
        section_ids = [clsViewSection.section_id for clsViewSection in clsSectionManager.view_sections.values()]
        self.assertEqual(len(set(section_ids)), 7)
        print("\n[TEST MULTI-SECTIONS]\n")
        print(f"Nombre de sections : {len(clsSectionManager.view_sections)}\n")
        for index, clsViewSection in enumerate(clsSectionManager.view_sections.values(), start=1):
            print(
                f"Section {index}\n"
                f"  section_id : {clsViewSection.section_id}\n"
                f"  file_name  : {clsViewSection.file_name}\n"
                f"  file_path  : {clsViewSection.file_path}\n"
            )
        print(f"Tous les section_id sont uniques : {len(set(section_ids)) == len(section_ids)}\n")


if __name__ == "__main__":
    unittest.main()
