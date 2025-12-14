# communicate_via_cohn.py/Open GoPro, Version 2.0 (C) Copyright 2021 GoPro, Inc. (http://gopro.com/OpenGoPro).
# This copyright was auto-generated on Wed Mar 27 22:05:49 UTC 2024

import sys
import json
import argparse
import asyncio
from base64 import b64encode
from pathlib import Path

import requests

from tutorial_modules import logger


MEDIA_SERVER = "http://10.5.5.9:8080/videos/DCIM"
DOWNLOAD_DIR = Path("./media")
CHUNK_SIZE = 1024 * 1024  # 1 MB

IP_ADDRESS: str = "192.168.0.109"
USERNAME: str = "gopro"
PASSWORD: str = "fn7INOh7rdVi"
TOKEN = b64encode(f"{USERNAME}:{PASSWORD}".encode("utf-8")).decode("ascii")
CERTIFICATE: Path = "/home/ihwee/temp/OpenGoPro/demos/python/tutorial/tutorial_modules/tutorial_9_cohn/cohn.crt"


async def download_file(directory: str, filename: str) -> None:
    download_url = f"https://{IP_ADDRESS}" + f"/videos/DCIM/{directory}/{filename}"
    logger.info(f"Downloading: {download_url}")

    out_path = DOWNLOAD_DIR / directory / filename
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with requests.get(download_url, stream=True, timeout=60, headers={"Authorization": f"Basic {TOKEN}"}, verify=CERTIFICATE) as r:
        r.raise_for_status()
        with open(out_path, "ab") as f:
            for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    f.write(chunk)


async def main() -> None:
    url = f"https://{IP_ADDRESS}" + "/gopro/media/list"
    logger.debug(f"Sending:  {url}")

    response = requests.get(
        url,
        timeout=10,
        headers={"Authorization": f"Basic {TOKEN}"},
        verify=CERTIFICATE,
    )
    # Check for errors (if an error is found, an exception will be raised)
    response.raise_for_status()
    logger.info("Command sent successfully")
    # Log response as json
    logger.info(f"Response: {json.dumps(response.json(), indent=4)}")
    media_list = response.json()

    for media in media_list.get("media", []):
        directory = media.get("d")

        for file_info in media.get("fs", []):
            filename = file_info.get("n")

            if not filename.lower().endswith(".mp4"):
                continue

            await download_file(directory, filename)

    logger.info("All downloads completed")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Demonstrate HTTPS communication via COHN.")
    args = parser.parse_args()

    try:
        asyncio.run(main())
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(e)
        sys.exit(-1)
    else:
        sys.exit(0)
