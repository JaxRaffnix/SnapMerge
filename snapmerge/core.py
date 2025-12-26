import os
import zipfile
import tempfile
from pathlib import Path
import shutil

from PIL import Image
from moviepy import VideoFileClip, ImageClip, CompositeVideoClip

from .helpers import _is_image, _get_image_extension, _get_media_and_overlay_file, _IMAGE_EXTS, _VIDEO_EXTS


# ___________________________________________________________________
# Combine Media in ZIP


def _process_zip(zip_path: Path, output_path: Path) -> Path:
    """
    Extracts and combines media files from a ZIP archive.
    
    Assumes the ZIP contains exactly two files: an overlay PNG and a media file
    (JPG, PNG, or MP4). Combines them and saves the result to the output path.

    Args:
        zip_path: Path to the ZIP file containing media and overlay files.
        output_path: Path where the combined media will be saved.

    Returns:
        Path to the output file.

    Raises:
        FileNotFoundError: If the ZIP file does not exist.
        ValueError: If the file is not a valid ZIP, is empty, or doesn't contain exactly 2 files.
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
        
        media, overlay = _get_media_and_overlay_file(Path(tmp))
        
        return combine_media(media, overlay, output_path)
    

# ___________________________________________________________________
# Core


def combine_media(media_path: Path, overlay_path: Path, output_path: Path) -> Path:
    """
    Combines a media file with a PNG overlay.
    
    Overlays a PNG image on top of a media file (image or video) and saves
    the result. For images, outputs a JPG. For videos, outputs an MP4 with
    the overlay positioned at center.

    Args:
        media_path: Path to the media file (JPG, PNG, or MP4).
        overlay_path: Path to the overlay PNG file.
        output_path: Path where the combined media will be saved.

    Returns:
        Path to the output file.

    Raises:
        FileNotFoundError: If media or overlay file does not exist.
        ValueError: If overlay is not PNG or media type is unsupported.
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


def process_data(input_dir: Path, output_dir: Path, overwrite: bool = False ):
    """
    Processes media files from the input directory and saves the results to the output directory.

    This function handles various types of media files, including:
    - MP4 and MOV video files, which are copied directly to the output directory.
    - Image files, which are copied with an additional extension added to the filename.
    - ZIP archives, which are unzipped, and the contained media files (JPG or MP4) are combined with an overlay PNG.
    - Folders containing media and overlay files, which are processed similarly to ZIP files.
    
    Args:
        input_dir (Path): The directory containing the media files to be processed.
        output_dir (Path): The directory where the processed files will be saved.
        overwrite (bool, optional): If True, existing files in the output directory will be overwritten. Defaults to False.
    
    Raises:
        ValueError: If the input directory does not exist or is not a directory.
        ValueError: If an unsupported file type is encountered during processing.
    
    Notes:
        - The function will skip files that already exist in the output directory unless `overwrite` is set to True.
        - The function currently supports MP4, MOV, JPG, and ZIP file types.
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
            _process_zip(input_dir / data, output_dir / data.replace(".zip", ""))

        elif (input_dir / data).is_dir():
            media, overlay = _get_media_and_overlay_file(input_dir / data)
            combine_media(media, overlay, output_dir / data)

        elif data.endswith("mp4") or data.endswith("mov"):
            shutil.copy2(input_dir / data, output_dir / data)

        elif _is_image(input_dir / data):
            ext = _get_image_extension(input_dir / data)
            shutil.copy2(input_dir / data, output_dir / f"{data}.{ext}")

        else:
            # warnings.warn(f"Unsupported file type: {data}", category=UserWarning)
            raise ValueError(f"Unsupported file type: {input_dir / data}")
        