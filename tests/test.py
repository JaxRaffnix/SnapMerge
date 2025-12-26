import unittest
from pathlib import Path
import tempfile

from snapmerge import process_data, combine_media

class TestSnapMerge(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for output
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_path = Path(self.temp_dir.name)
        self.test_data_dir = Path(__file__).parent / "test_data"

    def tearDown(self):
        # Clean up temporary directory
        self.temp_dir.cleanup()

    # def test_get_media_overlay(self):
    #     folder = self.test_data_dir / "example_folder"
    #     media, overlay = get_media_and_overlay_file(folder)
    #     self.assertTrue(media.exists())
    #     self.assertTrue(overlay.exists())
    #     self.assertIn("main", media.name)
    #     self.assertIn("overlay", overlay.name)

    # def test_combine_image(self):
    #     # Use a small image + overlay pair
    #     media = self.test_data_dir / "sample_image.jpg"
    #     overlay = self.test_data_dir / "overlay.png"
    #     output_file = self.output_path / "combined.jpg"
    #     combine_media(media, overlay, output_file)
    #     self.assertTrue(output_file.exists())
    #     self.assertTrue(output_file.suffix == ".jpg")

    # TODO: add cli test

    def test_process_data(self):
        # Test processing an entire directory
        input_dir = self.test_data_dir
        process_data(input_dir, self.output_path)
        # Check that output files exist
        output_files = list(self.output_path.iterdir())
        self.assertGreater(len(output_files), 0)

if __name__ == "__main__":
    unittest.main()
