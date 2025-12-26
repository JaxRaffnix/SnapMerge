"""
SnapMerge

This module reconstructs exported Snapchat media by combining the original
camera media (image or video) with its corresponding Snapchat overlay.
It is designed for use with data obtained from Snapchat's official
"Download My Data" export.

"""

from .core import process_data, combine_media
from .cli import *
