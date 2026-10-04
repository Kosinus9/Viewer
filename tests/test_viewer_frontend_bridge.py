import unittest
from unittest.mock import patch

from src.backend.application.CLS_LayoutManager import CLS_LayoutManager
from src.backend.application.CLS_SectionManager import CLS_SectionManager
from src.backend.application.CLS_TimerLifecycleManager import CLS_TimerLifecycleManager
from src.backend.application.CLS_ViewerController import CLS_ViewerController
from src.backend.domain.DUT.ENUM.E_CommandType import E_CommandType
from src.backend.domain.DUT.ENUM.E_FileType import E_FileType
from src.backend.domain.DUT.STRUCT.ST_Command import ST_Command
from src.backend.domain.DUT.STRUCT.ST_FrontendToBackendData import ST_FrontendToBackendData
from src.backend.infrastructure.CLS_FrontendBridge import CLS_FrontendBridge
from src.backend.infrastructure.renderers.CLS_PDFRenderer import CLS_PDFRenderer


class TestViewerFrontendBridge(unittest.TestCase):
    def setUp(self):
        self.clsLayoutManager = CLS_LayoutManager()
        self.clsLayoutManager.set_screen_dimensions(1920, 1080)
        self.clsSectionManager = CLS_SectionManager(self.clsLayoutManager)
        self.clsViewerController = CLS_ViewerController(self.clsSectionManager, CLS_TimerLifecycleManager(), CLS_FrontendBridge())
        self.addCleanup(patch.stopall)
        patch.object(CLS_PDFRenderer, "load", return_value=True).start()
        self.produced_data = []
        render_resource = CLS_PDFRenderer.render

        def observe_render(clsRenderer, *args, **kwargs):
            stBackendToFrontendData = render_resource(clsRenderer, *args, **kwargs)
            self.produced_data.append(stBackendToFrontendData)
            return stBackendToFrontendData

        patch.object(CLS_PDFRenderer, "render", autospec=True, side_effect=observe_render).start()

    def open_section(self, index):
        self.clsViewerController.process_command(
            ST_Command(E_CommandType.OPEN, f"provided-{index}.pdf", f"documents/actual-{index}.pdf")
        )

    def assert_prepared_data_identity(self, count):
        prepared_data = self.clsViewerController.frontend_bridge.get_backend_to_frontend_data()
        collected_data = self.clsSectionManager.get_backend_to_frontend_data()
        self.assertEqual(len(prepared_data), count)
        self.assertEqual(len(collected_data), count)
        for prepared, collected in zip(prepared_data, collected_data, strict=True):
            self.assertIs(prepared, collected)
            self.assertTrue(any(prepared is produced for produced in self.produced_data))
            self.assertIs(prepared.stJobLayout, self.clsSectionManager._stJobLayouts[prepared.section_id])
            self.assertIs(prepared.file_type, E_FileType.PDF)
        return prepared_data

    def test_controller_owns_one_bridge_and_manager_has_none(self):
        clsFrontendBridge = self.clsViewerController.frontend_bridge
        self.assertIsInstance(clsFrontendBridge, CLS_FrontendBridge)
        self.clsViewerController.interface_frontend_backend()
        self.open_section(1)
        self.assertIs(self.clsViewerController.frontend_bridge, clsFrontendBridge)
        self.assertEqual(sum(isinstance(value, CLS_FrontendBridge) for value in vars(self.clsViewerController).values()), 1)
        self.assertFalse(any(isinstance(value, CLS_FrontendBridge) for value in vars(self.clsSectionManager).values()))

    def test_open_transfers_single_renderer_result_without_reconstruction(self):
        self.open_section(1)
        prepared_data = self.assert_prepared_data_identity(1)
        self.assertIs(prepared_data[0], self.produced_data[0])
        self.assertEqual(prepared_data[0].file_name, "provided-1.pdf")
        self.assertEqual(prepared_data[0].file_path, "documents/actual-1.pdf")

    def test_multiple_sections_transfer_current_layouts_and_exclude_fifth(self):
        for index in range(1, 6):
            self.open_section(index)
            prepared_data = self.assert_prepared_data_identity(min(index, 4))
            self.assertEqual([data.file_name for data in prepared_data],
                             [f"provided-{number}.pdf" for number in range(1, min(index, 4) + 1)])

    def test_hide_show_close_keep_prepared_list_current_without_jobs(self):
        self.open_section(1)
        self.open_section(2)
        with patch.object(self.clsViewerController, "create_job") as create_job:
            for command_type, count in ((E_CommandType.HIDE, 1), (E_CommandType.SHOW, 2),
                                        (E_CommandType.CLOSE, 1)):
                self.clsViewerController.process_command(
                    ST_Command(command_type, "provided-1.pdf", "documents/actual-1.pdf")
                )
                self.assert_prepared_data_identity(count)
            self.clsViewerController.process_command(
                ST_Command(E_CommandType.CLOSE, "provided-2.pdf", "documents/actual-2.pdf")
            )
            self.assert_prepared_data_identity(0)
            create_job.assert_not_called()

    def test_interface_returns_frontend_input_without_routing_it(self):
        self.assertIsNone(self.clsViewerController.interface_frontend_backend())
        stFrontendToBackendData = ST_FrontendToBackendData("unregistered-section", "CLOSE")
        self.clsViewerController.frontend_bridge.set_frontend_to_backend_data(stFrontendToBackendData)
        with patch.object(self.clsViewerController, "process_command") as process_command:
            self.assertIs(self.clsViewerController.interface_frontend_backend(stFrontendToBackendData), stFrontendToBackendData)
            process_command.assert_not_called()
        self.assertEqual(stFrontendToBackendData.event, "CLOSE")
        self.assertEqual(self.clsSectionManager.view_sections, {})

    def test_directions_remain_independent(self):
        self.open_section(1)
        stFrontendToBackendData = ST_FrontendToBackendData("section-1", "unknown-event")
        self.clsViewerController.frontend_bridge.set_frontend_to_backend_data(stFrontendToBackendData)
        self.assertIs(self.clsViewerController.interface_frontend_backend(stFrontendToBackendData), stFrontendToBackendData)
        self.assert_prepared_data_identity(1)
        self.open_section(2)
        self.assertIs(self.clsViewerController.frontend_bridge.get_frontend_to_backend_data(), stFrontendToBackendData)
        self.assert_prepared_data_identity(2)

    def test_injected_bridge_immediately_calls_registered_controller_method(self):
        clsFrontendBridge = CLS_FrontendBridge()
        interface_method = CLS_ViewerController.interface_frontend_backend
        with patch.object(CLS_ViewerController, "interface_frontend_backend", autospec=True,
                          side_effect=interface_method) as interface, \
                patch.object(clsFrontendBridge, "get_frontend_to_backend_data") as get_frontend_data, \
                patch.object(self.clsSectionManager, "get_backend_to_frontend_data") as get_backend_data:
            clsViewerController = CLS_ViewerController(
                self.clsSectionManager, CLS_TimerLifecycleManager(), clsFrontendBridge
            )
            self.assertIs(clsViewerController.frontend_bridge, clsFrontendBridge)
            with patch.object(clsViewerController, "process_command") as process_command, \
                    patch.object(clsViewerController, "create_job") as create_job:
                for index, event in enumerate(("CLOSE", "SHOW", "unknown-event"), 1):
                    stFrontendToBackendData = ST_FrontendToBackendData("section-1", event)
                    clsFrontendBridge.receive_event(stFrontendToBackendData)
                    self.assertEqual(interface.call_count, index)
                    interface.assert_called_with(clsViewerController, stFrontendToBackendData)
                    self.assertIs(interface.call_args.args[1], stFrontendToBackendData)
                    self.assertEqual(stFrontendToBackendData.event, event)
                process_command.assert_not_called()
                create_job.assert_not_called()
            get_frontend_data.assert_not_called()
            get_backend_data.assert_not_called()


if __name__ == "__main__":
    unittest.main()
