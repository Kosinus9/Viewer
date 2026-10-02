import unittest
from unittest.mock import patch

import main
from src.backend.application.CLS_CommandManager import CLS_CommandManager
from src.backend.application.CLS_LayoutManager import CLS_LayoutManager
from src.backend.application.CLS_SectionManager import CLS_SectionManager
from src.backend.application.CLS_TimerLifecycleManager import CLS_TimerLifecycleManager
from src.backend.domain.DUT.ENUM.E_CommandType import E_CommandType


class TestMain(unittest.TestCase):
    def test_start_without_file_instantiates_components_without_command(self):
        with patch.object(main, "CLS_CommandManager") as command_manager, \
                patch.object(main, "CLS_ViewerController") as viewer_controller:
            main.main([])

        command_manager.assert_called_once_with()
        section_manager, layout_manager, timer_manager = viewer_controller.call_args.args
        self.assertIsInstance(section_manager, CLS_SectionManager)
        self.assertIsInstance(layout_manager, CLS_LayoutManager)
        self.assertIsInstance(timer_manager, CLS_TimerLifecycleManager)
        command_manager.return_value.create_open_command.assert_not_called()
        viewer_controller.return_value.process_command.assert_not_called()

    def test_file_is_passed_unchanged_and_returned_command_is_routed(self):
        file_path = r"C:\Viewer files\example.pdf"
        with patch.object(main, "CLS_CommandManager") as command_manager, \
                patch.object(main, "CLS_ViewerController") as viewer_controller, \
                patch("sys.argv", ["main.py", file_path]):
            main.main()

        command_manager.return_value.create_open_command.assert_called_once_with(file_path)
        viewer_controller.return_value.process_command.assert_called_once_with(
            command_manager.return_value.create_open_command.return_value
        )

    def test_real_command_manager_builds_open_command(self):
        file_path = "documents/example.pdf"
        with patch.object(main, "CLS_CommandManager", wraps=CLS_CommandManager) as command_manager, \
                patch.object(main, "CLS_ViewerController") as viewer_controller:
            main.main([file_path])

        command_manager.assert_called_once_with()
        command = viewer_controller.return_value.process_command.call_args.args[0]
        self.assertEqual(command.command_type, E_CommandType.OPEN)
        self.assertEqual(command.file_name, "example.pdf")
        self.assertEqual(command.file_path, file_path)


if __name__ == "__main__":
    unittest.main()
