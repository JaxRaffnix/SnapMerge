import tempfile
from pathlib import Path
import shutil
from contextlib import contextmanager

from PIL import Image
from moviepy import VideoFileClip, ImageClip, CompositeVideoClip

from .helpers import _is_image, _is_video, _is_media, _get_image_extension, _already_exists, _is_archive


# ___________________________________________________________________
# Find correct files


def get_media_and_overlay_file(dir_path: Path) -> tuple[Path, Path]:
    """
    Retrieve the media file and overlay file from the specified directory.

    This function searches for two specific types of files within the provided directory:
    - A media file, which must be an image or video file containing the substring "main" in its filename.
    - An overlay file, which must be an image file containing the substring "overlay" in its filename.

    Args:
        dir_path (Path): The directory path to search for the media and overlay files.
    
    Returns:
        tuple[Path, Path]: A tuple containing the paths to the media file and overlay file.
    
    Raises:
        ValueError: If the specified directory does not exist, is not a directory, 
                     or does not contain the required media and overlay files exactly once.
    """ 
    if not dir_path.exists() or not dir_path.is_dir():
        raise ValueError(f"Directory does not exist: {dir_path}")

    files = list(dir_path.iterdir())

    overlays = [f for f in files if "overlay" in f.name.lower() and _is_image(f)]
    if len(overlays) != 1:
        raise ValueError(f"Expected exactly 1 overlay file, found {len(overlays)} in {dir_path}")

    media = [f for f in files if "main" in f.name.lower() and _is_media(f)]
    if len(media) != 1:
        raise ValueError(f"Expected exactly 1 media file, found {len(media)} in {dir_path}")

    return media[0], overlays[0]


# ___________________________________________________________________
# Combine Media in ZIP

@contextmanager
def _unpack_archive(archive_path: Path):
    """
    Unpack an archive into a temporary directory and yield the directory path.

    The caller is responsible for processing the extracted files.
    The temporary directory is cleaned up automatically.
    """
    if not archive_path.exists() or not archive_path.is_file():
        raise FileNotFoundError(f"Archive dir not found: {archive_path}")
    if not _is_archive(archive_path):
        raise ValueError(f"Unsupported archive format: {archive_path}")

    with tempfile.TemporaryDirectory() as tmp:
        shutil.unpack_archive(str(archive_path), tmp)

        tmp_path = Path(tmp)
        if len(list(tmp_path.iterdir())) != 2:
            raise ValueError(f"Archive must contain exactly 2 files: {archive_path}")
        
        yield tmp_path


def combine_media(media_path: Path, overlay_path: Path, output_path: Path) -> Path:
    """
    Combines a media file with an overlay.
    
    Overlays an image on top of a media file (image or video) and saves
    the result. For images, the output type is inferred from the media type. For videos, outputs an MP4 with
    the overlay positioned at center. In both cases, the overlay is resized to match the media size if necessary.

    Args:
        media_path: Path to the media file (image or video).
        overlay_path: Path to the overlay file.
        output_path: Path where the combined media will be saved. May not include an extension!

    Returns:
        Path to the output file with the appropriate extension.

    Raises:
        FileNotFoundError: If media or overlay file does not exist.
    """
    if not media_path.exists() or not media_path.is_file():
        raise FileNotFoundError(f"Media file not found: {media_path}")
    if not overlay_path.exists() or not overlay_path.is_file():
        raise FileNotFoundError(f"Overlay file not found: {overlay_path}")
    if output_path.suffix != "":
        raise ValueError(f"Output path should not have an extension: {output_path}")
    # TODO: allow output format specification?
    
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if _is_image(media_path):    
        ext = _get_image_extension(media_path)

        with Image.open(overlay_path).convert("RGBA") as overlay:
            with Image.open(media_path).convert("RGBA") as media:
                if media.size != overlay.size:
                    overlay = overlay.resize(media.size)

                combined = Image.alpha_composite(media, overlay)
                output_path = output_path.with_suffix(f".{ext}")
                combined.convert("RGB").save(output_path)

    elif _is_video(media_path):
        video = VideoFileClip(media_path)
        with Image.open(overlay_path).convert("RGBA") as overlay:
            if video.size != overlay.size:
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
# Core Processing


def process_data(input_dir: Path, output_dir: Path, overwrite: bool = False ):
    """
    Processes media files from the input directory and saves the results to the output directory.

    This function handles various types of media files, including:
    - Video files, which are copied directly to the output directory.
    - Image files, which are copied with the missing extension added to the filename.
    - archive files, which are unzipped, and the contained media files (image or video) are combined with an overlay.
    - Folders containing media and overlay files, which are processed similarly to archives.
    
    Args:
        input_dir (Path): The directory containing the media files to be processed.
        output_dir (Path): The directory where the processed files will be saved.
        overwrite (bool, optional): If True, existing files in the output directory will be overwritten. Defaults to False.
    
    Raises:
        ValueError: If the input directory does not exist or is not a directory.
        ValueError: If an unsupported file type is encountered during processing.    
    """
    if not input_dir.exists() or not input_dir.is_dir():
        raise ValueError(f"Input directory does not exist: {input_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    for entry in input_dir.iterdir():
        base_name = entry.stem

        if _already_exists(base_name, output_dir) and not overwrite:
            continue

        if _is_archive(entry):
            with _unpack_archive(entry) as temp:
                media, overlay = get_media_and_overlay_file(temp)
                combine_media(media, overlay, output_dir / base_name)

        elif entry.is_dir():
            media, overlay = get_media_and_overlay_file(entry)
            combine_media(media, overlay, output_dir / base_name)

        elif _is_video(entry):
            shutil.copy2(entry, output_dir / entry.name)

        elif _is_image(entry):
            ext = _get_image_extension(entry)
            shutil.copy2(entry, output_dir / f"{entry.stem}.{ext}")

        else:
            raise ValueError(f"Unsupported file: {entry}")
        
    return True