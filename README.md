# SnapMerge

[SnapMerge](https://github.com/JaxRaffnix/SnapMerge) is a Python tool for merging Snapchat exported media. It combines media files with their overlay elements into a single file, making it easier to view and manage your Snapchat memories. Additionally, the directory is flattened for simpler organization and missing file extensions are added automatically.

This tool was last tested with the official Snapchat “Download My Data” export as of December 2025. If Snapchat changes its export format, please open an issue on [GitHub](https://github.com/JaxRaffnix/SnapMerge/issues).

## Example

Snapchat Export Folder:

```
snapchat_export/
├── image1
├── image2.zip/
│   ├── image2_main.jpg
│   └── image2_overlay.png
├── movie1.mp4
├── movie2.zip/
│   ├── movie2_main.mp4
│   └── movie2_overlay.png
...
```

Results after running SnapMerge `python -m snapmerge.cli ./snapchat_export ./merged_media`:

```
merged_media/
├── image1.jpg
├── image2.jpg
├── movie1.mp4
├── movie2.mp4
...
```

## Features

- **Archive Support** Automatically extracts archives supported by `shutil.unpack_archive` (e.g. ZIP, TAR)
- **Overlay Composition** Combines media files (image or video) with their corresponding overlay images using alpha compositing
- **File Copying** Copies standalone files directly to the output directory.
- **Extension Handling** Adds missing file extensions based on file type.
- **Overwrite Control** Option to skip existing files or overwrite them.


## Installation

SnapMerge requires [Python 3.7+](https://www.python.org/downloads/) or higher.

1. Clone the repository:
    ```bash
    git clone https://github.com/JaxRaffnix/SnapMerge.git
    cd SnapMerge
    ```

2. Create a virtual environment (optional but recommended):
   ```bash
   # Windows
   python -m venv .venv
   .\.venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

The media and overlay file inside a directory or archive are inferred dynamically based on their filenames:
- Overlay files must contain `"overlay"` in the filename
- Media files must contain `"main"` in the filename 

### Command Line Interface

Process your Snapchat export with a single command:

```bash
python -m snapmerge.cli <input_directory> <output_directory> [--overwrite]
```

**Arguments**
- `input_directory`: Path to the directory containing exported Snapchat media
- `output_directory`: Path where processed files will be saved  (created if it doesn't exist)

**Options**
- `--overwrite` or `-o`: Overwrite existing files in the output directory (default: skip)

**Example**
```bash
python -m snapmerge.cli ./snapchat_export ./merged_media --overwrite
```

### Python API

Use SnapMerge as a library in your own scripts:

```python
from pathlib import Path
from snapmerge import process_data

process_data(
    input_dir=Path("./snapchat_export"),
    output_dir=Path("./merged_media"),
    overwrite=True
)
```

The subfunctions `combine_media(media_path, overlay_path, output_path)` and `get_media_and_overlay_file(dir_path)` are also available for customization. For detailed usage, please refer to the relevant doc strings.

## License

See [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## Support

For issues or questions, please open an issue on the GitHub repository.

## Acknowledgements
AI language models were used extensively for boilerplate code generation and drafting documentation.
