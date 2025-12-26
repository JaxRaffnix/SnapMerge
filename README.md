# SnapMerge

SnapMerge is a Python Media Merger for Snapchat exported data. It combines media files with their overlay elements into single files, making it easier to view and manage your Snapchat memories. Additionally, the directory is flattened for simpler organization.

This tool was last tested with the official Snapchat “Download My Data” export as of December 2025. Should there be a change in Snapchat's export format, please open an issue on (GitHub)[https://github.com/JaxRaffnix/SnapMerge/issues].

## Example

Snapchat Download Folder:

```
my_data/
-- image1
-- movie1.mp4
-- image2.zip/
-- -- image2_main.jpg
-- -- image2_overlay.png
-- movie2.zip/
-- -- movie2_main.mp4
-- -- movie2_overlay.png
```

Results after running SnapMerge:

```
merged_data/
-- image1.jpg
-- movie1.mp4
-- image2.jpg
-- movie2.mp4
```

## Features

- **ZIP Support**: Automatically extracts and processes ZIP archives, if they contain a "...main..." media file (see file types below) and an "...overlay..." PNG
- **Image Merging**: Combines JPG/JPEG images with PNG overlays into single merged JPG files with alpha compositing
- **Video Merging**: Composites MP4 videos with PNG overlays, preserving audio and duration
- **Copy**: Overlaid media and standalone files are copied to the output directory
- **Overwrite Control**: Option to skip existing files or overwrite them

## Installation

### Requirements
- Python 3.7+

### Setup

1. Clone the repository:
```bash
git clone https://github.com/JaxRaffnix/SnapMerge.git
cd SnapMerge
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

media must be in one of the following formats and contain "main" in the filename:
- Images: JPG, JPEG
- Videos: MP4
Overlay file must be in PNG format and contain "overlay" in the filename.
 
Zip archive must contain exactly 2 files: one media file and one overlay file.

### Command Line

Run the CLI to process your Snapchat export:

```bash
python -m snapmerge.cli <input_directory> <output_directory> [options]
```

**Arguments:**
- `input_directory`: Path to the directory containing exported Snapchat media
- `output_directory`: Path where processed files will be saved

**Options:**
- `--overwrite` or `-o`: Overwrite existing files in the output directory (default: skip)

Example usage:
```bash
python -m snapmerge.cli ./snapchat_export ./merged_media --overwrite
```

### Python API

You can also use SnapMerge in your custom Python script:

```python
from pathlib import Path
from snapmerge.core import process_data

# Process media files
process_data(
    input_dir=Path("./snapchat_export"),
    output_dir=Path("./merged_media"),
    overwrite=True
)
```

The subfunction `combine_media(media_path, overlay_path, output_path)` is also available for more granular control in the module import. For detailed usage, please refer to the doc strings.

## Constrains and Assumptions

- The overwrite check compares file stems (names without extensions) in lowercase
- Overlay files should contain "overlay" in their filename
- Media files should contain "main" in their filename
- For videos, overlay positioning is centered
- Temporary files are cleaned up automatically

## Known Limitations

- Overlay resizing for videos may cause permission errors on some systems
- ZIP files must contain exactly 2 files (media and overlay)
- The overwrite check is case-insensitive but not extremely robust

## License

See [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## Support

For issues or questions, please open an issue on the GitHub repository.

## LLM
AI language models were used extensively for boilerplate code generation and documentation drafting.
