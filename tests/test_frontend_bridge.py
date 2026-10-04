import unittest

from src.backend.domain.DUT.ENUM.E_FileType import E_FileType
from src.backend.domain.DUT.STRUCT.ST_BackendToFrontendData import ST_BackendToFrontendData
from src.backend.domain.DUT.STRUCT.ST_JobLayout import ST_JobLayout
from src.backend.infrastructure.CLS_FrontendBridge import CLS_FrontendBridge


class TestFrontendBridge(unittest.TestCase):
    def setUp(self):
        self.clsFrontendBridge = CLS_FrontendBridge()

    def test_initial_data_is_empty(self):
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
