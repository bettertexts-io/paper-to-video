import os
from urllib.parse import quote
import requests
from constants import PEXELS_API_KEY

from script import Script, TextScriptScene, for_every_scene
from tmp import create_directories_from_path, tmp_content_scene_dir_path

def _get_first_video(query: str):
    headers = {
      'Authorization': PEXELS_API_KEY
    }
    
    res = requests.get(
        f"https://api.pexels.com/videos/search?query={quote(query)}&per_page=1&orientation=landscape&size=large",
        headers=headers,
    )

    files = res.json()["videos"][0]["video_files"]

    # Find the largest video wich is not larger than 1920 in width
    biggest = None
    biggest_width = 0
    for file in files:
        if file["width"] <= 1920 and file["width"] > biggest_width:
            biggest = file
            biggest_width = file["width"]

    return biggest["link"]

def _download_file(url, filename):
    # Send GET request
    response = requests.get(url, stream=True)
    
    # Check if the request was successful
    response.raise_for_status()

    # Write to file
    with open(filename, 'wb') as fd:
        for chunk in response.iter_content(chunk_size=8192):
            fd.write(chunk)
    

def generate_stock_footage(paper_id: str, script: Script):
    def _process_scene(context: [int, int], scene: TextScriptScene):
      query = scene["stockFootageQuery"]

      if not query:
          return None
      
      dir_path = tmp_content_scene_dir_path(paper_id=paper_id, section_id=context[0], scene_id=context[1])
      create_directories_from_path(dir_path)
      filename =  dir_path + "/stock_footage.mp4"

      if os.path.exists(filename):
          print("Stock footage for scene "f"{context[0]}.{context[1]}" " already exists")
          return filename
      
      url = _get_first_video(query)

      _download_file(url, filename)


      print("Downloaded stock footage for scene "f"{context[0]}.{context[1]}")

      return filename

    return for_every_scene(script, _process_scene)


if __name__ == "__main__":
    print(_get_first_video("nature"))
