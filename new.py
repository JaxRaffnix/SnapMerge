import os
import shutil
import zipfile
import tempfile
from pathlib import Path
import warnings

from PIL import Image
from moviepy import VideoFileClip, ImageClip, CompositeVideoClip


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



def _get_media_overlay(dir_path: Path) -> tuple[Path, Path]:
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


# ___________________________________________________________________
# Combine Media in ZIP


def process_zip(zip_path: Path, output_path: Path) -> Path:
    """
    Assuming zip contains an overlay png and a media file (jpg or mp4), combine them.    
    """
    if not zip_path.exists():
        raise FileNotFoundError(f"ZIP file not found: {zip_path}")
    if not zipfile.is_zipfile(zip_path) or zip_path.suffix.lower() != ".zip":
        raise ValueError(f"File is not a valid ZIP file: {zip_path}")
    if zip_path.stat().st_size == 0:
        raise ValueError(f"ZIP file is empty: {zip_path}")

    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(zip_path) as zip:
            zip.extractall(tmp)

        files = [Path(tmp) / f for f in os.listdir(tmp)]
        if len(files) != 2:
            raise ValueError(f"ZIP must contain exactly 2 files: {zip_path}")
        
        media, overlay = _get_media_overlay(Path(tmp))
        
        return combine_media(media, overlay, output_path)


def combine_media(media_path: Path, overlay_path: Path, output_path: Path):
    """
    Combines a media image or video with an overlay PNG and save the result.
    """
    if not media_path.exists() or not media_path.is_file():
        raise FileNotFoundError(f"Media file not found: {media_path}")
    if not overlay_path.exists() or not overlay_path.is_file():
        raise FileNotFoundError(f"Overlay file not found: {overlay_path}")
    if overlay_path.suffix.lower() != ".png":
        raise ValueError(f"Overlay file is not a PNG: {overlay_path}")
    if media_path.suffix.lower() not in _IMAGE_EXTS.union(_VIDEO_EXTS):
        raise ValueError(f"Unsupported media type: {media_path}")

    if _is_image(media_path):
        with Image.open(overlay_path).convert("RGBA") as overlay:
            with Image.open(media_path).convert("RGBA") as media:
                if media.size != overlay.size:
                    overlay = overlay.resize(media.size)

                combined = Image.alpha_composite(media, overlay)
                output_path = output_path.with_suffix(".jpg")
                combined.convert("RGB").save(output_path)

    elif media_path.suffix.lower() == ".mp4":
        video = VideoFileClip(media_path)
        with Image.open(overlay_path).convert("RGBA") as overlay:
            if overlay.size != video.size:
                overlay = overlay.resize(video.size)
        overlay_clip = ImageClip(overlay_path).with_duration(video.duration).with_position(("center", "center"))
        # .resize(newsize=video.size) #? this results in a permission error: "used by another process"

        final = CompositeVideoClip([video, overlay_clip])
        output_path = output_path.with_suffix(".mp4")
        final.write_videofile(
            output_path,
            audio=True
        )
        video.close()
        final.close()

    else:
        raise ValueError(f"Unsupported media type: {media_path}")
    

    return output_path

# ___________________________________________________________________
# Main

def process_data(input_dir: Path, output_dir: Path, overwrite: bool = False ):
    """
    Modifies snapchat media files and saves result in output dir. 

    - mp4 video files are copied
    - image files are copied and extension is added to filename
    - zip folders are unzipped, media (jpg or mp4) is combined with overlay png and saved as a single file
    - folders containing media and overlay are processed similarly to zip files
    """
    if not input_dir.exists() or not input_dir.is_dir():
        raise ValueError(f"Input directory does not exist: {input_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)
    existing = [f.lower().split(".")[0] for f in os.listdir(output_dir)]

    for data in os.listdir(input_dir):
        # TODO: Overwrite check is not very robust
        if data.lower().split(".")[0] in existing and not overwrite:
            continue

        if data.endswith("zip"):
            process_zip(input_dir / data, output_dir / data.replace(".zip", ""))

        elif (input_dir / data).is_dir():
            media, overlay = _get_media_overlay(input_dir / data)
            combine_media(media, overlay, output_dir / data)

        elif data.endswith("mp4") or data.endswith("mov"):
            shutil.copy2(input_dir / data, output_dir / data)

        elif _is_image(input_dir / data):
            ext = _get_image_extension(input_dir / data)
            shutil.copy2(input_dir / data, output_dir / f"{data}.{ext}")

        else:
            # warnings.warn(f"Unsupported file type: {data}", category=UserWarning)
            raise ValueError(f"Unsupported file type: {input_dir / data}")


process_data(Path("Snapchat"), Path("test_output"), overwrite=False)

# TODO: add CLI Interface
# TODO: add logging and logfile. remove some harsh exepctions, use wanrings instead
# TODO: add tests