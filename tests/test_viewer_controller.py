import unittest
from pathlib import Path
from unittest.mock import Mock, call, patch

from src.backend.application.CLS_CommandManager import CLS_CommandManager
from src.backend.application.CLS_LayoutManager import CLS_LayoutManager
from src.backend.application.CLS_SectionManager import CLS_SectionManager
from src.backend.application.CLS_TimerLifecycleManager import CLS_TimerLifecycleManager
from src.backend.application.CLS_ViewerController import CLS_ViewerController
from src.backend.domain.DUT.ENUM.E_CommandType import E_CommandType
from src.backend.domain.DUT.STRUCT.ST_Command import ST_Command


class TestViewerController(unittest.TestCase):
    def setUp(self):
        self.section_manager = CLS_SectionManager()
        self.layout_manager = CLS_LayoutManager()
        self.layout_manager.set_screen_dimensions(1920, 1080)
        self.controller = CLS_ViewerController(
            self.section_manager, self.layout_manager, CLS_TimerLifecycleManager()
        )
        self.file_path = str(Path("documents") / "example.pdf")
        self.file_name = "example.pdf"

    def test_command_manager_populates_file_identification(self):
        command = CLS_CommandManager().create_open_command(self.file_path)
        self.assertEqual(command.command_type, E_CommandType.OPEN)
        self.assertEqual(command.file_name, self.file_name)
        self.assertEqual(command.file_path, self.file_path)

    def test_open_job_uses_explicit_command_file_name(self):
        command = ST_Command(E_CommandType.OPEN, "explicit-name.pdf", self.file_path)
        job = self.controller.create_job(command)
        self.assertIsNotNone(job)
        self.assertEqual(job.stJobSection.file_name, command.file_name)
        self.assertEqual(job.stJobSection.file_path, command.file_path)

    def test_open_keeps_existing_job_flow(self):
        command = ST_Command(E_CommandType.OPEN, self.file_name, self.file_path)
        with patch.object(self.controller, "create_job", wraps=self.controller.create_job) as create_job:
            self.assertIsNone(self.controller.process_command(command))
            create_job.assert_called_once_with(command)

        job = self.controller.create_job(command)
        self.assertIsNotNone(job)
        self.assertEqual(job.command_type, E_CommandType.OPEN)
        self.assertEqual(job.stJobSection.file_name, "example.pdf")
        self.assertEqual(job.stJobSection.file_path, self.file_path)
        self.assertTrue(self.controller.validate_job(job))

    def test_routes_existing_sections_without_creating_jobs(self):
        for command_type, method_name in (
            (E_CommandType.SHOW, "show_section"),
            (E_CommandType.HIDE, "hide_section"),
            (E_CommandType.CLOSE, "close_section"),
        ):
            with self.subTest(command_type=command_type):
                manager = Mock(spec=CLS_SectionManager)
                manager.find_section.return_value = "existing-section"
                controller = CLS_ViewerController(manager, Mock(), Mock())
                with patch.object(controller, "create_job") as create_job:
                    controller.process_command(ST_Command(command_type, "explicit-name.pdf", self.file_path))
                    create_job.assert_not_called()
                self.assertEqual(manager.method_calls, [
                    call.find_section("explicit-name.pdf", self.file_path),
                    getattr(call, method_name)("existing-section"),
                ])

    def test_missing_section_does_not_trigger_an_action(self):
        for command_type in (E_CommandType.SHOW, E_CommandType.HIDE, E_CommandType.CLOSE):
            with self.subTest(command_type=command_type):
                manager = Mock(spec=CLS_SectionManager)
                manager.find_section.return_value = None
                controller = CLS_ViewerController(manager, Mock(), Mock())
                with patch.object(controller, "create_job") as create_job:
                    controller.process_command(ST_Command(command_type, "explicit-name.pdf", self.file_path))
                    create_job.assert_not_called()
                self.assertEqual(manager.method_calls, [
                    call.find_section("explicit-name.pdf", self.file_path),
                ])

    def test_file_path_selects_correct_section_and_close_removes_it(self):
        first_job = self.controller.create_job(ST_Command(E_CommandType.OPEN, self.file_name, self.file_path))
        other_path = str(Path("other") / "example.pdf")
        other_job = self.controller.create_job(ST_Command(E_CommandType.OPEN, self.file_name, other_path))
        first_id = self.section_manager.create_section(first_job)
        other_id = self.section_manager.create_section(other_job)
        section = self.section_manager.get_section(first_id)
        other_section = self.section_manager.get_section(other_id)

        with patch.object(section, "show") as show, patch.object(section, "hide") as hide, \
                patch.object(section, "close") as close, patch.object(other_section, "close") as other_close:
            self.controller.process_command(ST_Command(E_CommandType.SHOW, self.file_name, self.file_path))
            self.controller.process_command(ST_Command(E_CommandType.HIDE, self.file_name, self.file_path))
            self.controller.process_command(ST_Command(E_CommandType.CLOSE, self.file_name, self.file_path))
            show.assert_called_once_with()
            hide.assert_called_once_with()
            close.assert_called_once_with()
            other_close.assert_not_called()

        self.assertIsNone(self.section_manager.get_section(first_id))
        self.assertIs(self.section_manager.get_section(other_id), other_section)


if __name__ == "__main__":
    unittest.main()
