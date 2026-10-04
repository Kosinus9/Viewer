import unittest
from unittest.mock import patch

from src.backend.domain.CLS_ViewSection import CLS_ViewSection
from src.backend.domain.DUT.ENUM.E_FileType import E_FileType
from src.backend.domain.DUT.ENUM.E_ViewSectionState import E_ViewSectionState
from src.backend.domain.DUT.STRUCT.ST_BackendToFrontendData import ST_BackendToFrontendData
from src.backend.domain.DUT.STRUCT.ST_JobLayout import ST_JobLayout
from src.backend.infrastructure.renderers.CLS_PDFRenderer import CLS_PDFRenderer
from src.backend.infrastructure.renderers.CLS_ImageRenderer import CLS_ImageRenderer
from src.backend.infrastructure.renderers.CLS_VideoRenderer import CLS_VideoRenderer
from src.backend.infrastructure.renderers.CLS_TextRenderer import CLS_TextRenderer


class TestRendererFrontendData(unittest.TestCase):
    def test_each_renderer_constructs_its_family_contract(self):
        for renderer_class, file_type in (
            (CLS_PDFRenderer, E_FileType.PDF),
            (CLS_ImageRenderer, E_FileType.IMAGE),
            (CLS_VideoRenderer, E_FileType.VIDEO),
            (CLS_TextRenderer, E_FileType.TEXT),
        ):
            with self.subTest(renderer=renderer_class.__name__):
                clsRenderer = renderer_class()
                stJobLayout = ST_JobLayout(480, 270, 960, 540)
                stBackendToFrontendData = clsRenderer.render(
                    stJobLayout, section_id="section-1",
                    file_name="provided-name.bin", file_path="documents/different-name.resource",
                    file_type=file_type,
                )
                self.assertIsInstance(stBackendToFrontendData, ST_BackendToFrontendData)
                self.assertIs(stBackendToFrontendData.file_type, file_type)
                self.assertEqual(stBackendToFrontendData.section_id, "section-1")
                self.assertEqual(stBackendToFrontendData.file_name, "provided-name.bin")
                self.assertEqual(stBackendToFrontendData.file_path, "documents/different-name.resource")
                self.assertIs(stBackendToFrontendData.stJobLayout, stJobLayout)

    def test_renderers_preserve_received_type_without_inferring_it(self):
        for renderer_class in (CLS_PDFRenderer, CLS_ImageRenderer, CLS_VideoRenderer, CLS_TextRenderer):
            with self.subTest(renderer=renderer_class.__name__):
                clsRenderer = renderer_class()
                stJobLayout = ST_JobLayout(0, 0, 960, 540)
                stBackendToFrontendData = clsRenderer.render(
                    stJobLayout, section_id="section-1",
                    file_name="provided-name.txt", file_path="different-name.pdf",
                    file_type=E_FileType.UNKNOWN,
                )
                self.assertIs(stBackendToFrontendData.file_type, E_FileType.UNKNOWN)
                self.assertEqual(stBackendToFrontendData.file_name, "provided-name.txt")
                self.assertEqual(stBackendToFrontendData.file_path, "different-name.pdf")
                self.assertIs(stBackendToFrontendData.stJobLayout, stJobLayout)

    def test_show_relays_contract_from_existing_renderer(self):
        for suffix, renderer_class, file_type in (
            (".pdf", CLS_PDFRenderer, E_FileType.PDF),
            (".png", CLS_ImageRenderer, E_FileType.IMAGE),
            (".mp4", CLS_VideoRenderer, E_FileType.VIDEO),
            (".txt", CLS_TextRenderer, E_FileType.TEXT),
        ):
            for initial_state in (E_ViewSectionState.LOADING, E_ViewSectionState.BACKGROUND):
                with self.subTest(suffix=suffix, initial_state=initial_state):
                    file_path = "documents/actual-name" + suffix
                    clsViewSection = CLS_ViewSection("section-1", "provided-name.bin", file_path)
                    with patch.object(renderer_class, "load", return_value=True):
                        clsViewSection.initialize()
                    if initial_state == E_ViewSectionState.BACKGROUND:
                        clsViewSection.background()
                    clsRenderer = clsViewSection._clsRenderer
                    stJobLayout = ST_JobLayout(0, 0, 960, 540)
                    produced_data = []
                    render_resource = clsRenderer.render

                    def observe_render(*args, **kwargs):
                        stBackendToFrontendData = render_resource(*args, **kwargs)
                        produced_data.append(stBackendToFrontendData)
                        return stBackendToFrontendData

                    with patch.object(clsRenderer, "render", side_effect=observe_render) as render:
                        stBackendToFrontendData = clsViewSection.show(stJobLayout)
                        render.assert_called_once_with(
                            stJobLayout, section_id="section-1", file_name="provided-name.bin", file_path=file_path,
                            file_type=clsViewSection.file_type,
                        )
                    self.assertIs(clsViewSection.file_type, file_type)
                    self.assertIsInstance(clsRenderer, renderer_class)
                    self.assertIs(stBackendToFrontendData, produced_data[0])
                    self.assertIs(stBackendToFrontendData.file_type, file_type)
                    self.assertEqual(stBackendToFrontendData.section_id, clsViewSection.section_id)
                    self.assertEqual(stBackendToFrontendData.file_name, clsViewSection.file_name)
                    self.assertEqual(stBackendToFrontendData.file_path, clsViewSection.file_path)
                    self.assertIs(stBackendToFrontendData.stJobLayout, stJobLayout)
                    self.assertIs(clsViewSection._clsRenderer, clsRenderer)
                    self.assertIs(clsViewSection.state, E_ViewSectionState.VISIBLE)


if __name__ == "__main__":
    unittest.main()
