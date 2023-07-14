import fnmatch
import glob
import gzip
import logging
import os
import shutil
import tarfile
from typing import List
import requests

def arxiv_id_to_latex(paper_id: str) -> str:
    """Example id: 1706.03762"""

    dir_path = f"tmp/{paper_id}"
    archive_path = f"{dir_path}/arch.gz"
    res_path = f"{dir_path}/res"

    if os.path.exists(f"tmp/{paper_id}/latex.txt"):
        logging.info("Already downloaded this paper, returning cached version.")
        return read_file(f"tmp/{paper_id}/latex.txt")

    response = requests.get(f"https://arxiv.org/e-print/{paper_id}")
    content_type = response.headers["content-type"]

    if response.status_code != 200:
        logging.warn("Got a status code: " + str(response.status_code) + " while trying to download a paper.")
        return None

    logging.info("Content Type: " + content_type)
    logging.info("Status Code: " + str(response.status_code))
    logging.info("File Size: " + str(round(len(response.content) / 1024)) + " KB")

    if not os.path.exists(dir_path):
      os.mkdir(f"tmp/{paper_id}")

    if not os.path.exists(res_path):
      os.mkdir(res_path)

    with open(archive_path, "wb") as f:
        f.write(response.content)

    tar = tarfile.open(archive_path, "r:gz")
    tar.extractall(res_path)
    tar.close()

    os.remove(archive_path)

    latex = traverse_tex_file_contents(res_path)

    with open(f"{dir_path}/latex.txt", "w") as f:
        f.write(latex)

    return latex

def read_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content

def traverse_tex_file_contents(directory: str) -> str:
    # Use os.path.join and '**' to specify recursive search
    tex_file_paths = glob.glob(os.path.join(directory, '**', '*.tex'), recursive=True)

    tex_contents = []
    for file_path in tex_file_paths:
        tex_contents.append(read_file(file_path))

    tex_contents = order_by_input_occurrences(tex_contents)

    tex_files_content = "\n".join(tex_contents)

    return tex_files_content
    
    
def order_by_input_occurrences(arr: List[str]) -> List[str]:
    return sorted(arr, key=lambda x: x.count('\\input'), reverse=True)