import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from src.backend.domain.CLS_ViewSection import CLS_ViewSection
from src.backend.domain.DUT.ENUM.E_ViewSectionState import E_ViewSectionState
from src.backend.infrastructure.renderers.CLS_PDFRenderer import CLS_PDFRenderer
from src.backend.infrastructure.renderers.CLS_ImageRenderer import CLS_ImageRenderer
from src.backend.infrastructure.renderers.CLS_VideoRenderer import CLS_VideoRenderer
from src.backend.infrastructure.renderers.CLS_TextRenderer import CLS_TextRenderer


class TestRendererLoading(unittest.TestCase):
    def test_minimal_resource_preparation_returns_true(self):
        # These headers exercise minimal preparation, not full format validation.
        cases = (
            (CLS_PDFRenderer, ".pdf", b"%PDF-1.7\n%%EOF\n"),
            (CLS_ImageRenderer, ".jpg", b"\xff\xd8\xff\xe0"),
            (CLS_ImageRenderer, ".png", b"\x89PNG\r\n\x1a\n"),
            (CLS_ImageRenderer, ".bmp", b"BM"),
            (CLS_ImageRenderer, ".webp", b"RIFF\x04\x00\x00\x00WEBP"),
            (CLS_VideoRenderer, ".mp4", b"\x00\x00\x00\x18ftypisom"),
            (CLS_VideoRenderer, ".mov", b"\x00\x00\x00\x08wide\x00\x00\x00\x00"),
            (CLS_VideoRenderer, ".avi", b"RIFF\x04\x00\x00\x00AVI "),
            (CLS_VideoRenderer, ".mkv", b"\x1a\x45\xdf\xa3"),
            (CLS_VideoRenderer, ".webm", b"\x1a\x45\xdf\xa3"),
            (CLS_TextRenderer, ".txt", "Viewer : été".encode("utf-8")),
            (CLS_TextRenderer, ".text", b"\xef\xbb\xbfViewer"),
            (CLS_TextRenderer, ".txt", b""),
        )
        with TemporaryDirectory() as directory:
            for renderer_class, suffix, content in cases:
                with self.subTest(renderer=renderer_class.__name__, suffix=suffix, content=content):
                    file_path = Path(directory) / ("resource" + suffix)
                    file_path.write_bytes(content)
                    clsRenderer = renderer_class()
                    self.assertIs(clsRenderer.load(str(file_path)), True)

    def test_inaccessible_or_invalid_resources_return_false(self):
        with TemporaryDirectory() as directory:
            for renderer_class in (CLS_PDFRenderer, CLS_ImageRenderer, CLS_VideoRenderer, CLS_TextRenderer):
                with self.subTest(renderer=renderer_class.__name__):
                    clsRenderer = renderer_class()
                    self.assertIs(clsRenderer.load(str(Path(directory) / "missing")), False)
                    self.assertIs(clsRenderer.load(directory), False)
                    self.assertIs(clsRenderer.load("invalid\x00path"), False)
                    file_path = Path(directory) / "invalid"
                    file_path.write_bytes(b"\xffinvalid resource")
                    self.assertIs(clsRenderer.load(str(file_path)), False)
                    with patch("builtins.open", side_effect=PermissionError("access denied")):
                        self.assertIs(clsRenderer.load(str(file_path)), False)

    def test_empty_binary_resources_return_false(self):
        with TemporaryDirectory() as directory:
            file_path = Path(directory) / "empty"
            file_path.write_bytes(b"")
            for renderer_class in (CLS_PDFRenderer, CLS_ImageRenderer, CLS_VideoRenderer):
                with self.subTest(renderer=renderer_class.__name__):
                    clsRenderer = renderer_class()
                    self.assertIs(clsRenderer.load(str(file_path)), False)

    def test_supported_missing_resources_enter_error_and_keep_renderer(self):
        with TemporaryDirectory() as directory:
            for suffix, renderer_class in (
                (".pdf", CLS_PDFRenderer), (".png", CLS_ImageRenderer),
                (".mp4", CLS_VideoRenderer), (".txt", CLS_TextRenderer),
            ):
                with self.subTest(suffix=suffix):
                    file_path = str(Path(directory) / ("missing" + suffix))
                    clsViewSection = CLS_ViewSection("section-1", "original-name", file_path)
                    clsViewSection.initialize()
                    self.assertIsInstance(clsViewSection._clsRenderer, renderer_class)
                    self.assertIs(clsViewSection.state, E_ViewSectionState.ERROR)


if __name__ == "__main__":
    unittest.main()
