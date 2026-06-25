"""Minimal Bluesky XRPC client for image posts."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional
import os

import requests

from .config import BLUESKY_SERVICE


class BlueskyClient:
    def __init__(self, service: str = BLUESKY_SERVICE):
        self.service = service.rstrip("/")
        self.session = requests.Session()
        self.handle = os.environ.get("BSKY_HANDLE")
        self.password = os.environ.get("BSKY_APP_PASSWORD")
        self.did: Optional[str] = None
        self.access_jwt: Optional[str] = None

    def login(self) -> None:
        if not self.handle or not self.password:
            raise RuntimeError("BSKY_HANDLE and BSKY_APP_PASSWORD must be set")

        response = self.session.post(
            f"{self.service}/xrpc/com.atproto.server.createSession",
            json={"identifier": self.handle, "password": self.password},
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        self.did = payload["did"]
        self.access_jwt = payload["accessJwt"]
        self.session.headers.update({"Authorization": f"Bearer {self.access_jwt}"})

    def upload_blob(self, image_path: Path, mime_type: str) -> Dict:
        response = self.session.post(
            f"{self.service}/xrpc/com.atproto.repo.uploadBlob",
            headers={"Content-Type": mime_type, "Authorization": f"Bearer {self.access_jwt}"},
            data=image_path.read_bytes(),
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["blob"]

    def create_image_post(self, text: str, image_path: Path, alt_text: str, width: int, height: int, mime_type: str) -> Dict:
        if not self.did:
            raise RuntimeError("Call login() before posting")

        blob = self.upload_blob(image_path, mime_type)
        record = {
            "$type": "app.bsky.feed.post",
            "text": text,
            "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "embed": {
                "$type": "app.bsky.embed.images",
                "images": [
                    {
                        "alt": alt_text,
                        "image": blob,
                        "aspectRatio": {"width": width, "height": height},
                    }
                ],
            },
        }
        response = self.session.post(
            f"{self.service}/xrpc/com.atproto.repo.createRecord",
            json={"repo": self.did, "collection": "app.bsky.feed.post", "record": record},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

