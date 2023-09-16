import json
import os
from typing import Optional

script_dir = os.path.dirname(os.path.realpath(__file__))
tmp_dir_path = os.path.join(script_dir, "tmp")


tmp_sub_paths = {
    "archive": "arch.gz",
    "unarchDir": "unarch",
    "latex": "latex.tex",
    "barebone_script": "barebone.json",
    "script_with_scenes": "script_with_scenes.json",
    "script_with_scenes_refined": "script_with_scenes_refined.json",
    "summary": "summary.txt",
    "chromaDir": "chroma",
    "audio": "audio.mp3",
    "contentDir": "contentPieces",
    "output": "final.mp4",
}

tmp_scene_sub_paths = {
    "audio": "audio.mp3",
    "text_alignments": "audio_text_alignments.json",
    "stock_footage": "stock_footage",
    "caption_video": "caption_video.mov",
    "google_image": "google_image",
}


def tmp_paper_dir_path(paper_id: str):
    if not paper_id:
        raise Exception("Invalid paper_id for tmp_dir_path " + str(paper_id))

    return f"{tmp_dir_path}/{paper_id}"


def tmp_path(paper_id: str, kind: str):
    # create dir with a key of type type
    # only return the path

    dir_path = tmp_paper_dir_path(paper_id)

    if not kind:
        return dir_path

    if kind in tmp_sub_paths:
        return f"{dir_path}/{tmp_sub_paths[kind]}"
    else:
        raise Exception("Invalid type for tmp_path " + str(kind))


def tmp_scene_path(paper_id: str, section_id: int, scene_id: int, kind: Optional[str]):
    dir_path = tmp_content_scene_dir_path(paper_id, section_id, scene_id)

    if not kind:
        return dir_path

    if kind in tmp_scene_sub_paths:
        return f"{dir_path}/{tmp_scene_sub_paths[kind]}"
    else:
        raise Exception("Invalid type for tmp_path " + str(kind))


def tmp_content_scene_dir_path(paper_id: str, section_id: int, scene_id: int):
    return f"{tmp_path(paper_id, 'contentDir')}/{section_id}/{scene_id}"


def tmp_loader(paper_id: str, kind: Optional[str], save_type: Optional[str]):
    path = tmp_path(paper_id, kind)

    if not os.path.exists(path):
        return None

    if save_type == "json":
        with open(path, "r") as f:
            return json.load(f)
    elif save_type == "raw":
        with open(path, "rb") as f:
            return f.read()
    elif save_type == "str":
        with open(path, "r") as f:
            return f.read()


def tmp_saver(paper_id: str, kind: Optional[str], data, save_type: Optional[str]):
    path = tmp_path(paper_id, kind)

    if not os.path.exists(tmp_dir_path):
        os.mkdir(tmp_dir_path)

    # recursively create dirs
    if not os.path.exists(tmp_paper_dir_path(paper_id)):
        os.mkdir(tmp_paper_dir_path(paper_id))

    if "Dir" in kind:
        if not os.path.exists(path):
            os.mkdir(path)

    try:
        if save_type == "json":
            with open(path, "w") as f:
                json.dump(data, f, indent=4)
        elif save_type == "raw":
            with open(path, "wb") as f:
                f.write(data)
        elif save_type == "str":
            with open(path, "w") as f:
                f.write(data)
        else:
            raise Exception("Invalid save_type for tmp_saver " + str(save_type))

    except Exception as e:
        print(f"Failed to save data to {path}: {e}")

    return path


def create_directories_from_path(path):
    try:
        # Split the path into components based on '/'
        components = path.split("/")

        # Build the path component by component
        current_path = "/" if path.startswith("/") else "."
        for component in components:
            # Skip empty components
            if component:
                current_path = os.path.join(current_path, component)

                # Check if the directory exists, if not create it
                if not os.path.exists(current_path):
                    os.makedirs(current_path)
                    print(f"Created: {current_path}")
    except Exception as e:
        print(f"Failed to create directories from path {path}: {e}")
