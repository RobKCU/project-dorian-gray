"""Image steps: the first frame, the daily edit (OpenAI or a free mock), JPEG
re-saving, and Bluesky-safe preparation."""

from io import BytesIO
from pathlib import Path
from typing import Dict, List, Tuple
import base64
import hashlib
import os
import time

from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import requests

from .config import CHAIN_JPEG_QUALITY, IMAGE_MODEL, IMAGE_POST_LIMIT_BYTES, IMAGE_QUALITY, IMAGE_SIZE


def _target_size() -> Tuple[int, int]:
    w, h = IMAGE_SIZE.lower().split("x")
    return int(w), int(h)


def save_jpeg(image: Image.Image, path: Path, quality: int = CHAIN_JPEG_QUALITY) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(path, format="JPEG", quality=quality)
    return path


def first_frame(base_path: Path, out_path: Path) -> Path:
    """Day 1: the base photo, cropped/resized to the working size. No other change."""
    with Image.open(base_path) as original:
        image = ImageOps.exif_transpose(original).convert("RGB")
        image = ImageOps.fit(image, _target_size(), Image.Resampling.LANCZOS, centering=(0.5, 0.4))
    return save_jpeg(image, out_path)


def resave(prev_path: Path, out_path: Path) -> Path:
    """A quiet day: re-encode yesterday's JPEG (one more generation of loss)."""
    with Image.open(prev_path) as im:
        return save_jpeg(im.copy(), out_path)


def openai_edit(prev_path: Path, prompt: str, raw_out: Path) -> Path:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set (put it in .env)")
    image_bytes = prev_path.read_bytes()
    data = {"model": IMAGE_MODEL, "prompt": prompt, "size": IMAGE_SIZE, "quality": IMAGE_QUALITY, "n": "1"}

    response, last_error = None, None
    for attempt in range(1, 4):
        try:
            response = requests.post(
                "https://api.openai.com/v1/images/edits",
                headers={"Authorization": f"Bearer {api_key}"},
                files={"image": (prev_path.name, image_bytes, "image/jpeg")},
                data=data,
                timeout=300,
            )
            if response.status_code < 500:
                break
            last_error = RuntimeError(f"OpenAI server error {response.status_code}")
        except requests.exceptions.RequestException as exc:
            last_error = exc
        if attempt < 3:
            time.sleep(15 * attempt)

    if response is None:
        raise RuntimeError(f"OpenAI image edit failed after retries: {last_error}")
    if response.status_code != 200:
        try:
            detail = response.json().get("error", {}).get("message", response.text)
        except ValueError:
            detail = response.text
        raise RuntimeError(f"OpenAI image edit failed: {detail}")

    info = response.json()["data"][0]
    if "b64_json" in info:
        out = base64.b64decode(info["b64_json"])
    else:
        r = requests.get(info["url"], timeout=60)
        r.raise_for_status()
        out = r.content
    raw_out.parent.mkdir(parents=True, exist_ok=True)
    raw_out.write_bytes(out)
    return raw_out


def mock_edit(prev_path: Path, moves: List[Dict], raw_out: Path) -> Path:
    """Free stand-in for testing the pipeline: a small deterministic change per move."""
    with Image.open(prev_path) as im:
        image = im.convert("RGB")
    for move in moves:
        s = 0.04 + 0.08 * move["strength"]
        seed = int(hashlib.md5(move["id"].encode()).hexdigest()[:6], 16)
        kind = seed % 4
        if kind == 0:
            image = ImageEnhance.Color(image).enhance(1 - s if "glo" in move["id"] else 1 + s)
        elif kind == 1:
            image = image.filter(ImageFilter.GaussianBlur(radius=0.4 + 2 * s))
        elif kind == 2:
            image = ImageEnhance.Contrast(image).enhance(1 + s)
        else:
            image = ImageEnhance.Brightness(image).enhance(1 - s / 2)
    raw_out.parent.mkdir(parents=True, exist_ok=True)
    image.save(raw_out, format="PNG")
    return raw_out


def to_chain_jpeg(raw_path: Path, out_path: Path) -> Path:
    with Image.open(raw_path) as im:
        image = im.convert("RGB")
        if image.size != _target_size():
            image = ImageOps.fit(image, _target_size(), Image.Resampling.LANCZOS)
        return save_jpeg(image, out_path)


def prepare_for_bluesky(source: Path, out_path: Path) -> Tuple[Path, int, int, str]:
    with Image.open(source) as original:
        image = ImageOps.exif_transpose(original).convert("RGB")
    for quality in (92, 86, 80, 74, 68):
        buf = BytesIO()
        image.save(buf, format="JPEG", quality=quality, optimize=True)
        if len(buf.getvalue()) <= IMAGE_POST_LIMIT_BYTES:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(buf.getvalue())
            return out_path, image.width, image.height, "image/jpeg"
    raise RuntimeError("Could not compress image under Bluesky's size limit")
