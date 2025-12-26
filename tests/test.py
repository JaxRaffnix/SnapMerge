import unittest
from pathlib import Path
import tempfile

from snapmerge import process_data, combine_media

class TestSnapMerge(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_path = Path(self.temp_dir.name)
        # self.output_path = Path(__file__).parent / "test_output"
        self.test_data_dir = Path(__file__).parent / "test_data"

    def tearDown(self):
        self.temp_dir.cleanup()

    # TODO: add cli test

    def test_process_data(self):
        process_data(self.test_data_dir, self.output_path)
        output_files = list(self.output_path.iterdir())
        self.assertEqual(len(output_files), 5, "Should result in 5 data items.")

if __name__ == "__main__":
    unittest.main()
