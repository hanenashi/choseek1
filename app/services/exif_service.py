from fractions import Fraction
from pathlib import Path

from PIL import Image, ExifTags


TAG_NAMES = {value: key for key, value in ExifTags.TAGS.items()}


def _load_exif_data(image_path: Path) -> tuple[dict, dict]:
    try:
        with Image.open(image_path) as image:
            exif = image.getexif()
            exif_ifd = exif.get_ifd(ExifTags.IFD.Exif)
            return dict(exif), dict(exif_ifd)
    except Exception:
        return {}, {}


def _get_exif_value(exif_data: tuple[dict, dict], tag_name: str):
    tag_id = TAG_NAMES.get(tag_name)
    if tag_id is None:
        return None

    root_exif, camera_exif = exif_data
    return camera_exif.get(tag_id) or root_exif.get(tag_id)


def _to_fraction(value) -> Fraction | None:
    if value is None:
        return None
    if isinstance(value, (tuple, list)) and len(value) == 2:
        numerator, denominator = value
        if denominator == 0:
            return None
        return Fraction(numerator, denominator)
    return Fraction(value)


def _format_shutter(value) -> str:
    if value is None:
        return "Unknown"

    fraction = _to_fraction(value)
    if fraction is None:
        return "Unknown"

    fraction = fraction.limit_denominator(8000)
    if fraction.denominator == 1:
        return f"{fraction.numerator}s"
    if fraction.numerator == 1:
        return f"1/{fraction.denominator}s"
    return f"{float(fraction):.3g}s"


def _format_aperture(value) -> str:
    if value is None:
        return "Unknown"

    aperture_fraction = _to_fraction(value)
    if aperture_fraction is None:
        return "Unknown"

    aperture = float(aperture_fraction)
    if aperture <= 0:
        return "Unknown"

    return f"f/{aperture:.1f}".replace(".0", "")


def _format_iso(value) -> str:
    if value is None:
        return "Unknown"
    if isinstance(value, (tuple, list)):
        value = value[0] if value else None
    return str(value) if value is not None else "Unknown"


def build_exif_tooltip(image_path: Path, base_name: str) -> str:
    exif_data = _load_exif_data(image_path)

    shot_time = (
        _get_exif_value(exif_data, "DateTimeOriginal")
        or _get_exif_value(exif_data, "DateTimeDigitized")
        or _get_exif_value(exif_data, "DateTime")
        or "Unknown"
    )
    shutter = _format_shutter(_get_exif_value(exif_data, "ExposureTime"))
    iso = _format_iso(
        _get_exif_value(exif_data, "ISOSpeedRatings")
        or _get_exif_value(exif_data, "PhotographicSensitivity")
    )
    aperture = _format_aperture(_get_exif_value(exif_data, "FNumber"))

    return "\n".join(
        [
            base_name,
            f"Shot time: {shot_time}",
            f"Shutter: {shutter}",
            f"ISO: {iso}",
            f"Aperture: {aperture}",
        ]
    )
