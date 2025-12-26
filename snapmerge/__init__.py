"""
SnapMerge

[SnapMerge](https://github.com/JaxRaffnix/SnapMerge) is a Python tool for merging Snapchat exported media. It combines media files with their overlay elements into a single file, making it easier to view and manage your Snapchat memories. Additionally, the directory is flattened for simpler organization and missing file extensions are added.

This tool was last tested with the official Snapchat “Download My Data” export as of December 2025. If Snapchat changes its export format, please open an issue on [GitHub](https://github.com/JaxRaffnix/SnapMerge/issues).
"""

from .core import process_data, combine_media, get_media_and_overlay_file
# from .cli import *
