import os
from bs4 import Script
from serpapi import GoogleSearch
import requests
import shutil
from PIL import Image


from .constants import SERP_API_KEY
from .script import TextScriptScene, for_every_scene
from .tmp import tmp_scene_path

valid_file_extensions = ["jpg", "png", "gif", "jpeg"]


def fetch_image(searchQuery: str, filenameWithoutExtension: str):
    params = {
        "q": searchQuery,
        "tbm": "isch",
        "ijn": "0",
        "location": "San Francisco,California,United States",
        "hl": "en",
        "gl": "us",  # Changed from 'en' to 'us' to fix the 'Unsupported `en` country - gl parameter.' error
        "google_domain": "google.de",
        "api_key": SERP_API_KEY,
        "filetype": "|".join(
            valid_file_extensions
        ),  # Constructed from valid_file_extensions
        "tbs": "isz:lt,islt:2mp",  # Added to filter for big files (larger than 2MP)
    }

    client = GoogleSearch(params)
    results = client.get_dict()

    filename = None

    for result in results["images_results"]:
        try:
            image_url = result["original"]

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            }
            response = requests.get(image_url, headers=headers, stream=True)

            response.raise_for_status()

            file_extension = response.headers["content-type"].split("/")[-1]

            if file_extension not in valid_file_extensions:
                continue

            filename = f"{filenameWithoutExtension}.{file_extension}"

            with open(filename, "wb") as out_file:
                shutil.copyfileobj(response.raw, out_file)
            del response

            return filename

        except Exception as e:
            print(e)
            continue


def fetch_google_images(paper_id: str, script: Script):
    def _process_scene(context: tuple[int, int], scene: TextScriptScene):
        query = scene["stockFootageQuery"]

        if not query:
            return None

        filenameWithoutExtension = tmp_scene_path(
            paper_id=paper_id,
            section_id=context[0],
            scene_id=context[1],
            kind="google_image",
        )

        # Check for files with any extension
        for ext in ["jpg", "png", "gif", "webp", "jpeg"]:
            filename = f"{filenameWithoutExtension}.{ext}"
            if os.path.exists(filename):
                print(
                    "Google image for scene "
                    f"{context[0]}.{context[1]}"
                    " already exists"
                )
                return filename

        filename = fetch_image(query, filenameWithoutExtension=filenameWithoutExtension)

        print("Downloaded google image for scene " f"{context[0]}.{context[1]}")

        return filename

    return for_every_scene(script, _process_scene)


if __name__ == "__main__":
    fetch_image("Machine learning concept animation", "test_filename.jpg")
