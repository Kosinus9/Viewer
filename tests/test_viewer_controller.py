import unittest

from src.backend.infrastructure.CLS_FrontendBridge import CLS_FrontendBridge
from pathlib import Path
from unittest.mock import Mock, call, patch

from src.backend.application.CLS_CommandManager import CLS_CommandManager
from src.backend.application.CLS_LayoutManager import CLS_LayoutManager
from src.backend.application.CLS_SectionManager import CLS_SectionManager
from src.backend.application.CLS_TimerLifecycleManager import CLS_TimerLifecycleManager
from src.backend.application.CLS_ViewerController import CLS_ViewerController
from src.backend.domain.DUT.ENUM.E_CommandType import E_CommandType
from src.backend.domain.DUT.STRUCT.ST_Command import ST_Command
from src.backend.domain.DUT.STRUCT.ST_JobLayout import ST_JobLayout


class TestViewerController(unittest.TestCase):
    def setUp(self):
        self.clsSectionManager = CLS_SectionManager(CLS_LayoutManager())
        self.clsTimerLifecycleManager = CLS_TimerLifecycleManager()
        self.clsViewerController = CLS_ViewerController(
            self.clsSectionManager, self.clsTimerLifecycleManager, CLS_FrontendBridge()
        )
        self.file_path = str(Path("documents") / "example.pdf")
        self.file_name = "example.pdf"

    def test_command_manager_populates_file_identification(self):
        command = CLS_CommandManager().create_open_command(self.file_path)
        self.assertEqual(command.command_type, E_CommandType.OPEN)
        self.assertEqual(command.file_name, self.file_name)
        self.assertEqual(command.file_path, self.file_path)

    def test_create_job_without_layout_manager_initializes_zero_layout(self):
        self.assertIs(self.clsViewerController.section_manager, self.clsSectionManager)
        self.assertIs(self.clsViewerController.timer_lifecycle_manager, self.clsTimerLifecycleManager)
        stCommand = ST_Command(E_CommandType.OPEN, self.file_name, self.file_path)
        stJob = self.clsViewerController.create_job(stCommand)
        self.assertIsNotNone(stJob)
        self.assertEqual(stJob.stJobLayout, ST_JobLayout(0, 0, 0, 0))
        self.assertTrue(self.clsViewerController.validate_job(stJob))

    def test_validate_job_requires_nonnegative_integers_for_all_layout_fields(self):
        stCommand = ST_Command(E_CommandType.OPEN, self.file_name, self.file_path)
        stJob = self.clsViewerController.create_job(stCommand)
        for field_name in ("position_x", "position_y", "width", "height"):
            for value, expected_validity in ((-1, False), (0, True), (1, True), (True, False), (1.0, False), (None, False), ("0", False)):
                with self.subTest(field=field_name, value=value):
                    stJob.stJobLayout = ST_JobLayout(0, 0, 0, 0)
                    setattr(stJob.stJobLayout, field_name, value)
                    self.assertIs(self.clsViewerController.validate_job(stJob), expected_validity)

    def test_open_job_uses_explicit_command_file_name(self):
        command = ST_Command(E_CommandType.OPEN, "explicit-name.pdf", self.file_path)
        job = self.clsViewerController.create_job(command)
        self.assertIsNotNone(job)
        self.assertEqual(job.stJobSection.file_name, command.file_name)
        self.assertEqual(job.stJobSection.file_path, command.file_path)

    def test_open_keeps_existing_job_flow(self):
        command = ST_Command(E_CommandType.OPEN, self.file_name, self.file_path)
        with patch.object(self.clsViewerController, "create_job", wraps=self.clsViewerController.create_job) as create_job:
            self.assertIsNone(self.clsViewerController.process_command(command))
            create_job.assert_called_once_with(command)

        job = self.clsViewerController.create_job(command)
        self.assertIsNotNone(job)
        self.assertEqual(job.command_type, E_CommandType.OPEN)
        self.assertEqual(job.stJobSection.file_name, "example.pdf")
        self.assertEqual(job.stJobSection.file_path, self.file_path)
        self.assertTrue(self.clsViewerController.validate_job(job))

    def test_open_passes_same_validated_job_and_preserves_section_id(self):
        command = ST_Command(E_CommandType.OPEN, self.file_name, self.file_path)
        job = self.clsViewerController.create_job(command)
        with patch.object(self.clsViewerController, "create_job", return_value=job) as create_job, \
                patch.object(self.clsSectionManager, "create_section", wraps=self.clsSectionManager.create_section) as create_section:
            self.assertIsNone(self.clsViewerController.process_command(command))

        create_job.assert_called_once_with(command)
        create_section.assert_called_once_with(job)
        self.assertIs(create_section.call_args.args[0], job)
        self.assertEqual(len(self.clsSectionManager.view_sections), 1)
        clsViewSection = self.clsSectionManager.get_section(job.stJobSection.section_id)
        self.assertIsNotNone(clsViewSection)
        self.assertEqual(clsViewSection.section_id, job.stJobSection.section_id)
        self.assertEqual(clsViewSection.file_name, job.stJobSection.file_name)
        self.assertEqual(clsViewSection.file_path, job.stJobSection.file_path)

    def test_open_does_not_create_section_when_job_cannot_be_built_or_validated(self):
        stCommand = ST_Command(E_CommandType.OPEN, self.file_name, self.file_path)
        with patch.object(self.clsViewerController, "create_job", return_value=None), \
                patch.object(self.clsSectionManager, "create_section") as create_section:
            self.clsViewerController.process_command(stCommand)
            create_section.assert_not_called()
        for file_name in ("", None):
            with self.subTest(file_name=file_name):
                stCommand = ST_Command(E_CommandType.OPEN, file_name, self.file_path)
                with patch.object(self.clsSectionManager, "create_section") as create_section:
                    self.assertIsNone(self.clsViewerController.process_command(stCommand))
                    create_section.assert_not_called()
        self.assertEqual(self.clsSectionManager.view_sections, {})

    def test_routes_existing_sections_without_creating_jobs(self):
        for command_type, method_name in (
            (E_CommandType.SHOW, "show_section"),
            (E_CommandType.HIDE, "hide_section"),
            (E_CommandType.CLOSE, "close_section"),
        ):
            with self.subTest(command_type=command_type):
                clsSectionManager = Mock(spec=CLS_SectionManager)
                clsSectionManager.find_section.return_value = "existing-section"
                clsSectionManager.get_backend_to_frontend_data.return_value = []
                clsViewerController = CLS_ViewerController(clsSectionManager, Mock(), CLS_FrontendBridge())
                with patch.object(clsViewerController, "create_job") as create_job:
                    clsViewerController.process_command(ST_Command(command_type, "explicit-name.pdf", self.file_path))
                    create_job.assert_not_called()
                self.assertEqual(clsSectionManager.method_calls, [
                    call.find_section("explicit-name.pdf", self.file_path),
                    getattr(call, method_name)("existing-section"),
                    call.get_backend_to_frontend_data(),
                ])

    def test_missing_section_does_not_trigger_an_action(self):
        for command_type in (E_CommandType.SHOW, E_CommandType.HIDE, E_CommandType.CLOSE):
            with self.subTest(command_type=command_type):
                clsSectionManager = Mock(spec=CLS_SectionManager)
                clsSectionManager.find_section.return_value = None
                clsViewerController = CLS_ViewerController(clsSectionManager, Mock(), CLS_FrontendBridge())
                with patch.object(clsViewerController, "create_job") as create_job:
                    clsViewerController.process_command(ST_Command(command_type, "explicit-name.pdf", self.file_path))
                    create_job.assert_not_called()
                self.assertEqual(clsSectionManager.method_calls, [
                    call.find_section("explicit-name.pdf", self.file_path),
                ])

    def test_file_path_selects_correct_section_and_close_removes_it(self):
        first_job = self.clsViewerController.create_job(ST_Command(E_CommandType.OPEN, self.file_name, self.file_path))
        other_path = str(Path("other") / "example.pdf")
        other_job = self.clsViewerController.create_job(ST_Command(E_CommandType.OPEN, self.file_name, other_path))
        self.clsSectionManager._clsLayoutManager.set_screen_dimensions(1920, 1080)
        with patch("src.backend.infrastructure.renderers.CLS_PDFRenderer.CLS_PDFRenderer.load", return_value=True):
            first_id = self.clsSectionManager.create_section(first_job)
            other_id = self.clsSectionManager.create_section(other_job)
        self.clsSectionManager.hide_section(first_id)
        clsViewSection = self.clsSectionManager.get_section(first_id)
        clsOtherViewSection = self.clsSectionManager.get_section(other_id)

        with patch.object(clsViewSection, "show") as show, patch.object(clsViewSection, "hide") as hide, \
                patch.object(clsViewSection, "close") as close, patch.object(clsOtherViewSection, "close") as other_close:
            self.clsViewerController.process_command(ST_Command(E_CommandType.SHOW, self.file_name, self.file_path))
            stJobLayout = self.clsSectionManager._stJobLayouts[first_id]
            self.clsViewerController.process_command(ST_Command(E_CommandType.HIDE, self.file_name, self.file_path))
            self.clsViewerController.process_command(ST_Command(E_CommandType.CLOSE, self.file_name, self.file_path))
            show.assert_called_once_with(stJobLayout)
            hide.assert_called_once_with()
            close.assert_called_once_with()
            other_close.assert_not_called()

        self.assertIsNone(self.clsSectionManager.get_section(first_id))
        self.assertIs(self.clsSectionManager.get_section(other_id), clsOtherViewSection)


if __name__ == "__main__":
    unittest.main()
