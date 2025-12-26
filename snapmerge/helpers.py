import os
from pathlib import Path
from moviepy import VideoFileClip
from PIL import Image


# ___________________________________________________________________
# Constants


# ___________________________________________________________________
# Image and Video Identifier


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
    

def _is_video(video_path: Path) -> bool:
    if not video_path.exists() or not video_path.is_file():
        return False

    try:
        clip = VideoFileClip(video_path)
        clip.close()
        return True
    except Exception:
        return False
    

def _is_media(path: Path) -> bool:
    return _is_image(path) or _is_video(path)


# ___________________________________________________________________
# Check Duplicates


def _already_exists(name: Path, output_dir: Path) -> bool:
    """
    Check whether a file with the given base name already exists in the output
    directory, regardless of file extension.
    """
    name = name.stem.lower()

    return any(f.is_file() and f.stem.lower() == name for f in output_dir.iterdir())


# ___________________________________________________________________
# Archive Checker

def _is_archive(path: Path) -> bool:
    """Check if the given path is a supported archive file and is valid."""
    EXT = {".zip", ".tar", ".tar.gz", ".tgz"}
    return path.suffix.lower() in EXT