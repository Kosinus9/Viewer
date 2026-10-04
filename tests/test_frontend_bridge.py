import unittest

from src.backend.domain.DUT.ENUM.E_FileType import E_FileType
from src.backend.domain.DUT.STRUCT.ST_BackendToFrontendData import ST_BackendToFrontendData
from src.backend.domain.DUT.STRUCT.ST_FrontendToBackendData import ST_FrontendToBackendData
from src.backend.domain.DUT.STRUCT.ST_JobLayout import ST_JobLayout
from src.backend.infrastructure.CLS_FrontendBridge import CLS_FrontendBridge


class TestFrontendBridge(unittest.TestCase):
    def setUp(self):
        self.clsFrontendBridge = CLS_FrontendBridge()

    def test_initial_data_is_empty(self):
        self.assertEqual(self.clsFrontendBridge.get_backend_to_frontend_data(), [])

    def test_receive_event_without_callback_preserves_structure(self):
        stFrontendToBackendData = ST_FrontendToBackendData("section-1", "CLOSE")
        self.clsFrontendBridge.receive_event(stFrontendToBackendData)
        self.assertIs(self.clsFrontendBridge.get_frontend_to_backend_data(), stFrontendToBackendData)

    def test_receive_event_notifies_synchronously_after_storing_each_event(self):
        received_data = []

        def callback(stFrontendToBackendData):
            self.assertIs(self.clsFrontendBridge.get_frontend_to_backend_data(), stFrontendToBackendData)
            received_data.append(stFrontendToBackendData)

        self.clsFrontendBridge.set_event_callback(callback)
        for index, event in enumerate(("CLOSE", "SHOW", "unknown-event"), 1):
            stFrontendToBackendData = ST_FrontendToBackendData("section-1", event)
            self.clsFrontendBridge.receive_event(stFrontendToBackendData)
            self.assertEqual(len(received_data), index)
            self.assertIs(received_data[-1], stFrontendToBackendData)
            self.assertEqual(stFrontendToBackendData.event, event)

    def test_existing_setter_uses_same_event_notification(self):
        received_data = []
        self.clsFrontendBridge.set_event_callback(received_data.append)
        stFrontendToBackendData = ST_FrontendToBackendData("section-1", "HIDE")
        self.clsFrontendBridge.set_frontend_to_backend_data(stFrontendToBackendData)
        self.assertEqual(len(received_data), 1)
        self.assertIs(received_data[0], stFrontendToBackendData)

    def test_initial_frontend_data_is_absent(self):
        self.assertIsNone(self.clsFrontendBridge.get_frontend_to_backend_data())

    def test_receives_frontend_structure_and_preserves_data(self):
        stFrontendToBackendData = ST_FrontendToBackendData("section-1", "CLOSE")
        self.clsFrontendBridge.set_frontend_to_backend_data(stFrontendToBackendData)
        self.assertIs(self.clsFrontendBridge.get_frontend_to_backend_data(), stFrontendToBackendData)
        self.assertEqual(stFrontendToBackendData.section_id, "section-1")
        self.assertEqual(stFrontendToBackendData.event, "CLOSE")
        self.assertIs(self.clsFrontendBridge.get_frontend_to_backend_data(), stFrontendToBackendData)

    def test_new_frontend_data_replaces_previous_data(self):
        stPreviousData = ST_FrontendToBackendData("previous", "HIDE")
        stNewData = ST_FrontendToBackendData("new", "SHOW")
        self.clsFrontendBridge.set_frontend_to_backend_data(stPreviousData)
        self.clsFrontendBridge.set_frontend_to_backend_data(stNewData)
        self.assertIs(self.clsFrontendBridge.get_frontend_to_backend_data(), stNewData)
        self.assertEqual(stPreviousData.event, "HIDE")

    def test_frontend_events_are_transported_without_interpretation(self):
        for event in ("CLOSE", "SHOW", "HIDE", "OPEN", "unknown-event", ""):
            with self.subTest(event=event):
                stFrontendToBackendData = ST_FrontendToBackendData("unregistered-section", event)
                self.clsFrontendBridge.set_frontend_to_backend_data(stFrontendToBackendData)
                self.assertIs(self.clsFrontendBridge.get_frontend_to_backend_data(), stFrontendToBackendData)
                self.assertEqual(stFrontendToBackendData.section_id, "unregistered-section")
                self.assertEqual(stFrontendToBackendData.event, event)
                self.assertEqual(self.clsFrontendBridge.get_backend_to_frontend_data(), [])

    def test_directions_remain_independent(self):
        stBackendToFrontendData = ST_BackendToFrontendData(
            E_FileType.TEXT, "section-1", "a.txt", "a.txt", ST_JobLayout(0, 0, 960, 540)
        )
        stFrontendToBackendData = ST_FrontendToBackendData("section-1", "CLOSE")
        self.clsFrontendBridge.set_backend_to_frontend_data([stBackendToFrontendData])
        self.assertIsNone(self.clsFrontendBridge.get_frontend_to_backend_data())
        self.clsFrontendBridge.set_frontend_to_backend_data(stFrontendToBackendData)
        self.assertIs(self.clsFrontendBridge.get_backend_to_frontend_data()[0], stBackendToFrontendData)
        self.clsFrontendBridge.set_backend_to_frontend_data([])
        self.assertIs(self.clsFrontendBridge.get_frontend_to_backend_data(), stFrontendToBackendData)
        self.assertEqual(self.clsFrontendBridge.get_backend_to_frontend_data(), [])

    def test_receives_one_structure_and_preserves_data(self):
        stJobLayout = ST_JobLayout(480, 270, 960, 540)
        stBackendToFrontendData = ST_BackendToFrontendData(
            E_FileType.TEXT, "section-1", "provided-name.txt", "documents/different-name.txt", stJobLayout
        )
        self.clsFrontendBridge.set_backend_to_frontend_data([stBackendToFrontendData])
        prepared_data = self.clsFrontendBridge.get_backend_to_frontend_data()
        self.assertEqual(len(prepared_data), 1)
        self.assertIs(prepared_data[0], stBackendToFrontendData)
        self.assertIs(prepared_data[0].file_type, E_FileType.TEXT)
        self.assertEqual(prepared_data[0].section_id, "section-1")
        self.assertEqual(prepared_data[0].file_name, "provided-name.txt")
        self.assertEqual(prepared_data[0].file_path, "documents/different-name.txt")
        self.assertIs(prepared_data[0].stJobLayout, stJobLayout)

    def test_receives_multiple_structures_without_four_element_limit(self):
        for count in (2, 4, 7):
            with self.subTest(count=count):
                stBackendToFrontendData = [
                    ST_BackendToFrontendData(
                        E_FileType.PDF, f"section-{index}", "document.pdf", "documents/document.pdf",
                        ST_JobLayout(index, 0, 960, 540),
                    )
                    for index in range(count)
                ]
                self.clsFrontendBridge.set_backend_to_frontend_data(stBackendToFrontendData)
                prepared_data = self.clsFrontendBridge.get_backend_to_frontend_data()
                self.assertEqual(len(prepared_data), count)
                for received, prepared in zip(stBackendToFrontendData, prepared_data, strict=True):
                    self.assertIs(prepared, received)
                    self.assertIs(prepared.stJobLayout, received.stJobLayout)

    def test_new_data_replaces_previous_data(self):
        stJobLayout = ST_JobLayout(0, 0, 960, 540)
        stPreviousData = ST_BackendToFrontendData(E_FileType.PDF, "previous", "a.pdf", "a.pdf", stJobLayout)
        stNewData = ST_BackendToFrontendData(E_FileType.IMAGE, "new", "b.png", "b.png", stJobLayout)
        self.clsFrontendBridge.set_backend_to_frontend_data([stPreviousData])
        self.clsFrontendBridge.set_backend_to_frontend_data([stNewData])
        prepared_data = self.clsFrontendBridge.get_backend_to_frontend_data()
        self.assertEqual(len(prepared_data), 1)
        self.assertIs(prepared_data[0], stNewData)

    def test_empty_list_clears_prepared_data(self):
        stBackendToFrontendData = ST_BackendToFrontendData(
            E_FileType.PDF, "section-1", "a.pdf", "a.pdf", ST_JobLayout(0, 0, 960, 540)
        )
        self.clsFrontendBridge.set_backend_to_frontend_data([stBackendToFrontendData])
        self.clsFrontendBridge.set_backend_to_frontend_data([])
        self.assertEqual(self.clsFrontendBridge.get_backend_to_frontend_data(), [])

    def test_external_list_changes_do_not_change_prepared_data(self):
        stBackendToFrontendData = ST_BackendToFrontendData(
            E_FileType.PDF, "section-1", "a.pdf", "a.pdf", ST_JobLayout(0, 0, 960, 540)
        )
        supplied_data = [stBackendToFrontendData]
        self.clsFrontendBridge.set_backend_to_frontend_data(supplied_data)
        supplied_data.clear()
        exposed_data = self.clsFrontendBridge.get_backend_to_frontend_data()
        self.assertEqual(len(exposed_data), 1)
        self.assertIs(exposed_data[0], stBackendToFrontendData)
        exposed_data.clear()
        self.assertIs(self.clsFrontendBridge.get_backend_to_frontend_data()[0], stBackendToFrontendData)


if __name__ == "__main__":
    unittest.main()
