import unittest
from pathlib import Path
import tempfile
import shutil
from PIL import Image

from snapmerge import process_data, combine_media, get_media_and_overlay_file

class TestSnapMerge(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_path = Path(self.temp_dir.name)
        self.test_data_dir = Path(__file__).parent / "test_data"

        # Create a temp media file
        self.image_path = self.output_path / "image_main.png"
        Image.new("RGBA", (100, 100), (255, 0, 0, 255)).save(self.image_path)
        self.overlay_path = self.output_path / "image_overlay.png"
        Image.new("RGBA", (100, 100), (0, 255, 0, 128)).save(self.overlay_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    # -----------------------------
    # Test get_media_and_overlay_file
    # -----------------------------
    def test_get_media_and_overlay_file(self):
        temp_folder = Path(self.output_path / "folder")
        temp_folder.mkdir()
        shutil.copy2(self.image_path, temp_folder / "image_main.png")
        shutil.copy2(self.overlay_path, temp_folder / "image_overlay.png")

        media, overlay = get_media_and_overlay_file(temp_folder)
        self.assertTrue(media.name.endswith("main.png"))
        self.assertTrue(overlay.name.endswith("overlay.png"))

    # -----------------------------
    # Test combine_media
    # -----------------------------
    def test_combine_image_media(self):
        output_file = self.output_path / "combined"
        combined_path = combine_media(self.image_path, self.overlay_path, output_file)
        self.assertTrue(combined_path.exists())
        self.assertTrue(combined_path.suffix in [".png", ".jpg"])

    # -----------------------------
    # Test processing a temp ZIP archive
    # -----------------------------
    # def test_process_archive_zip(self):
    #     temp_zip = self.output_path / "archive.zip"
    #     with zipfile.ZipFile(temp_zip, "w") as zipf:
    #         zipf.write(self.image_path, arcname="image_main.png")
    #         zipf.write(self.overlay_path, arcname="image_overlay.png")

    #     # _process_archive returns output_path after combining
    #     output_file = self.output_path / "output_combined"
    #     combined_path = _process_archive(temp_zip, output_file)
    #     self.assertTrue(combined_path.exists())
    #     self.assertTrue(combined_path.suffix in [".png", ".jpg"])

    # -----------------------------
    # Test process_data end-to-end
    # -----------------------------
    def test_process_data(self):
        # Copy sample files into input folder
        input_dir = Path(self.output_path / "input")
        input_dir.mkdir()
        shutil.copy2(self.image_path, input_dir / "image_main.png")
        shutil.copy2(self.overlay_path, input_dir / "image_overlay.png")

        process_data(input_dir, self.output_path)
        output_files = list(self.output_path.iterdir())
        self.assertGreaterEqual(len(output_files), 2)

    # -----------------------------
    # Test overwrite behavior
    # -----------------------------
    def test_overwrite_flag(self):
        # Create a dummy media file in the output directory
        dummy_file = self.output_path / "image_main.png"
        dummy_file.write_text("original")  # known content

        # Run process_data with overwrite=False
        process_data(self.test_data_dir, self.output_path, overwrite=False)

        # File content should remain unchanged
        content_after_skip = dummy_file.read_text()
        self.assertEqual(content_after_skip, "original", "File should not be overwritten when overwrite=False")

        # Run process_data with overwrite=True
        process_data(self.test_data_dir, self.output_path, overwrite=True)

        # File content should now be updated
        content_after_overwrite = dummy_file.read_text()
        self.assertNotEqual(content_after_overwrite, "original", "File should be overwritten when overwrite=True")


    def test_cli(self):
        # TODO: add cli test
        pass


if __name__ == "__main__":
    unittest.main()
