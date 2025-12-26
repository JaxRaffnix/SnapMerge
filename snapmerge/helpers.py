import os
from pathlib import Path
from PIL import Image


# ___________________________________________________________________
# Constants


_IMAGE_EXTS = {".jpg", ".jpeg", ".png"}
_VIDEO_EXTS = {".mp4"}


# ___________________________________________________________________
# Helpers


def _get_image_extension(image_path: Path) -> str:
    """"Return image file extension based on its format."""
    if not image_path.exists() or not _is_image(image_path):
        raise ValueError(f"File is not an image or doesn't exist: {image_path}")
    
    with Image.open(image_path) as image:
        return image.format.lower()


def _is_image(image_path: Path) -> bool:
    if not image_path.exists() or not image_path.is_file():
        return False
    
    try:
        with Image.open(image_path):
            return True
    except Exception:
        return False


def _get_media_and_overlay_file(dir_path: Path) -> tuple[Path, Path]:
    """
    Given a directory path, return the media file (jpg or mp4) and overlay png file.
    """
    if not dir_path.exists() or not dir_path.is_dir():
        raise ValueError(f"Directory does not exist: {dir_path}")

    media_file = None
    overlay_file = None

    for file in os.listdir(dir_path):
        file_path = dir_path / file
        if _is_image(file_path) and file_path.suffix.lower() == ".png" and "overlay" in file.lower():
            overlay_file = file_path
        elif file_path.suffix.lower() in _IMAGE_EXTS.union(_VIDEO_EXTS) and "main" in file.lower():
            media_file = file_path

    if media_file is None or overlay_file is None:
        raise ValueError(f"Directory must contain 'main' media and 'overlay' PNG files: {dir_path}")

    return media_file, overlay_file