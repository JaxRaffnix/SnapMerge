import os
import shutil
from pathlib import Path
import warnings


from .helpers import _is_image, _get_image_extension, _get_media_overlay
from .merge import process_zip, combine_media


# ___________________________________________________________________
# Core


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