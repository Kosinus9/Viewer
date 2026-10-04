import unittest

from src.backend.domain.DUT.ENUM.E_RenderName import E_RenderName

from src.backend.domain.DUT.STRUCT.ST_BackendToFrontendData import ST_BackendToFrontendData
from src.backend.domain.DUT.STRUCT.ST_FrontendToBackendData import ST_FrontendToBackendData
from src.backend.domain.DUT.STRUCT.ST_JobLayout import ST_JobLayout


class TestFrontendDataStructures(unittest.TestCase):
    def test_render_names_and_contract_preserve_each_render_type(self):
        self.assertEqual(
            list(E_RenderName),
            [E_RenderName.PDF, E_RenderName.IMAGE, E_RenderName.VIDEO, E_RenderName.TEXT],
        )
        for render_name in E_RenderName:
            with self.subTest(render_name=render_name):
                stJobLayout = ST_JobLayout(0, 0, 960, 540)
                stBackendToFrontendData = ST_BackendToFrontendData(
                    render_name, "section-1", "provided-name", "documents/resource", stJobLayout
                )
                self.assertIs(stBackendToFrontendData.renderer_name, render_name)
                self.assertIs(stBackendToFrontendData.stJobLayout, stJobLayout)

    def test_backend_to_frontend_preserves_data_and_layout_identity(self):
        stJobLayout = ST_JobLayout(480, 270, 960, 540)
        stBackendToFrontendData = ST_BackendToFrontendData(
            renderer_name=E_RenderName.PDF,
            section_id="section-1",
            file_name="provided-name.pdf",
            file_path="documents/document.pdf",
            stJobLayout=stJobLayout,
        )
        self.assertIs(stBackendToFrontendData.renderer_name, E_RenderName.PDF)
        self.assertEqual(stBackendToFrontendData.section_id, "section-1")
        self.assertEqual(stBackendToFrontendData.file_name, "provided-name.pdf")
        self.assertEqual(stBackendToFrontendData.file_path, "documents/document.pdf")
        self.assertIs(stBackendToFrontendData.stJobLayout, stJobLayout)

    def test_frontend_to_backend_preserves_section_and_event(self):
        stFrontendToBackendData = ST_FrontendToBackendData(
            section_id="section-1",
            event="test-event",
        )
        self.assertEqual(stFrontendToBackendData.section_id, "section-1")
        self.assertEqual(stFrontendToBackendData.event, "test-event")


if __name__ == "__main__":
    unittest.main()
