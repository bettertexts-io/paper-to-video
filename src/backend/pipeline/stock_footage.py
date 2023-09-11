import logging
import os
from typing import Optional
from urllib.parse import quote
import requests
import subprocess

from .constants import PEXELS_API_KEY
from .script import Script, TextScriptScene, for_every_scene
from .tmp import (
    create_directories_from_path,
    tmp_content_scene_dir_path,
    tmp_scene_path,
)


# Check duration of the audio file
def check_media_duration(audio_filename):
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            audio_filename,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return float(result.stdout)


def _get_stock_videos(query: str, filename: str, min_duration: Optional[int] = None):
    headers = {"Authorization": PEXELS_API_KEY}

    page = 1
    total_duration = 0
    video_count = 0
    artist_videos = {}

    filenames = []
    while total_duration < min_duration:
        try:
            res = requests.get(
                f"https://api.pexels.com/videos/search?query={quote(query)}&per_page=1&page={page}&orientation=landscape&size=large",
                headers=headers,
            )

            res.raise_for_status()
            video_data = res.json()["videos"][0]

        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to fetch stock videos: {e}")
            page += 1
            continue

        if video_data:
            artist_id = video_data["user"]["id"]

            # Ensure there is only one video per artist
            if artist_id in artist_videos:
                page += 1
                continue
            artist_videos[artist_id] = True

            # Get the video duration from the video data
            video_duration = video_data["duration"]
            total_duration += video_duration

            # Find the largest video which is not larger than 1920 in width
            biggest = None
            biggest_width = 0
            for file in video_data["video_files"]:
                if file["width"] <= 1920 and file["width"] > biggest_width:
                    biggest = file
                    biggest_width = file["width"]

            # Download the video
            video_count += 1
            video_filename = f"{filename}.{video_count}.mp4"
            _download_file(biggest["link"], video_filename)
            filenames.append(video_filename)

        # Go to the next page
        page += 1

    return filenames


def _download_file(url, filename):
    try:
        # Send GET request
        response = requests.get(url, stream=True)

        # Check if the request was successful
        response.raise_for_status()

        # Write to file
        with open(filename, "wb") as fd:
            for chunk in response.iter_content(chunk_size=8192):
                fd.write(chunk)

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to download file: {e}")


def generate_stock_footage(paper_id: str, script: Script):
    def _process_scene(context: tuple[int, int], scene: TextScriptScene):
        query = scene["stockFootageQuery"]

        if not query:
            return None

        dir_path = tmp_content_scene_dir_path(
            paper_id=paper_id, section_id=context[0], scene_id=context[1]
        )
        create_directories_from_path(dir_path)

        audio_filename = tmp_scene_path(
            paper_id=paper_id, section_id=context[0], scene_id=context[1], kind="audio"
        )

        audio_duration = check_media_duration(audio_filename)
        print(f"Duration of audio file: {audio_duration} seconds")
        filename = dir_path + "/stock_footage"

        if os.path.exists(filename):
            print(
                "Stock footage for scene "
                f"{context[0]}.{context[1]}"
                " already exists"
            )
            return filename

        _get_stock_videos(query, filename, min_duration=audio_duration)

        print("Downloaded stock footage for scene " f"{context[0]}.{context[1]}")

        return filename

    return for_every_scene(script, _process_scene)


if __name__ == "__main__":
    print(_get_stock_videos("nature", "test", 60))
