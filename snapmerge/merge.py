import os
import zipfile
import tempfile
from pathlib import Path
import warnings

from PIL import Image
from moviepy import VideoFileClip, ImageClip, CompositeVideoClip

from .helpers import _is_image, _get_media_overlay, _IMAGE_EXTS, _VIDEO_EXTS

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