"""OpenAI image editing and Bluesky-safe image preparation."""

from io import BytesIO
from pathlib import Path
from typing import Tuple
import base64
import os
import time

from PIL import Image, ImageOps
import requests

from .config import BASE_PORTRAIT_PATH, IMAGE_POST_LIMIT_BYTES


def generate_portrait(prompt: str, output_path: Path) -> Path:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    if not BASE_PORTRAIT_PATH.exists():
        raise RuntimeError(f"Base portrait is missing: {BASE_PORTRAIT_PATH}")

    with BASE_PORTRAIT_PATH.open("rb") as image_file:
        files = {"image": ("base_portrait.jpg", image_file.read(), "image/jpeg")}

    response = None
    last_error = None
    for attempt in range(1, 4):
        try:
            response = requests.post(
                "https://api.openai.com/v1/images/edits",
                headers={"Authorization": f"Bearer {api_key}"},
                files=files,
                data={"model": "gpt-image-1", "prompt": prompt, "size": "1024x1024", "n": 1},
                timeout=180,
            )
            if response.status_code < 500:
                break
            last_error = RuntimeError(f"OpenAI server error {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as exc:
            last_error = exc
        if attempt < 3:
            time.sleep(10 * attempt)

    if response is None:
        raise RuntimeError(f"OpenAI image generation failed after retries: {last_error}")
    if response.status_code != 200:
        try:
            detail = response.json().get("error", {}).get("message", response.text)
        except ValueError:
            detail = response.text
        raise RuntimeError(f"OpenAI image generation failed: {detail}")

    payload = response.json()
    image_info = payload["data"][0]
    if "b64_json" in image_info:
        image_bytes = base64.b64decode(image_info["b64_json"])
    elif "url" in image_info:
        image_response = requests.get(image_info["url"], timeout=60)
        image_response.raise_for_status()
        image_bytes = image_response.content
    else:
        raise RuntimeError("OpenAI returned an unrecognized image payload")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(image_bytes)
    return output_path


def prepare_jpeg_for_bluesky(source_path: Path, output_path: Path) -> Tuple[Path, int, int, str]:
    """Strip metadata and compress a JPEG under Bluesky's current 2 MB image limit."""
    with Image.open(source_path) as original:
        image = ImageOps.exif_transpose(original).convert("RGB")
        width, height = image.size

        for max_side in (1024, 960, 896, 832, 768):
            candidate = image
            if max(width, height) > max_side:
                scale = max_side / max(width, height)
                candidate = image.resize((int(width * scale), int(height * scale)), Image.Resampling.LANCZOS)

            for quality in (92, 86, 80, 74, 68):
                buffer = BytesIO()
                candidate.save(buffer, format="JPEG", quality=quality, optimize=True)
                data = buffer.getvalue()
                if len(data) <= IMAGE_POST_LIMIT_BYTES:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_bytes(data)
                    return output_path, candidate.width, candidate.height, "image/jpeg"

    raise RuntimeError("Could not compress generated JPEG under Bluesky's image size limit")
