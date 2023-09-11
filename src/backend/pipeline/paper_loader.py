import fnmatch
import glob
import gzip
import logging
import os
import re
import shutil
import tarfile
from typing import List

import requests

from .tmp import tmp_loader, tmp_path, tmp_saver

logging.basicConfig(level=logging.DEBUG)


def paper_id_to_latex(paper_id: str) -> str:
    """Example id: 1706.03762"""

    latex = tmp_loader(paper_id=paper_id, kind="latex", save_type="str")

    if latex:
        print("Already downloaded this paper, returning cached version.")
        return latex

    response = requests.get(f"https://arxiv.org/e-print/{paper_id}")
    content_type = response.headers["content-type"]

    if response.status_code != 200:
        logging.warn(
            "Got a status code: "
            + str(response.status_code)
            + " while trying to download a paper."
        )
        return None

    print("Content Type: " + content_type)
    print("Status Code: " + str(response.status_code))
    print("File Size: " + str(round(len(response.content) / 1024)) + " KB")

    tmp_saver(paper_id=paper_id, kind="archive", data=response.content, save_type="raw")

    archive_path = tmp_path(paper_id=paper_id, kind="archive")
    res_path = tmp_path(paper_id=paper_id, kind="unarchDir")

    tar = tarfile.open(archive_path, "r:gz")
    tar.extractall(res_path)
    tar.close()

    os.remove(archive_path)

    latex = traverse_tex_file_contents(res_path)

    tmp_saver(paper_id=paper_id, kind="latex", data=latex, save_type="str")

    return latex


def read_file(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    return content


def traverse_tex_file_contents(directory: str) -> str:
    # Use os.path.join and '**' to specify recursive search
    tex_file_paths = glob.glob(os.path.join(directory, "**", "*.tex"), recursive=True)

    tex_contents = []
    for file_path in tex_file_paths:
        tex_contents.append([get_filename(file_path), read_file(file_path)])

    tex_contents = order_by_input_occurrences(tex_contents)

    tex_files_content = replace_imports(tex_contents)

    return tex_files_content[0][1]


def order_by_input_occurrences(arr: List[List[str]]) -> List[List[str]]:
    return sorted(arr, key=lambda x: x[1].count("\\input"), reverse=True)


def get_filename(path: str) -> str:
    match = re.search(r"\/?([^/]*?)(?=\.[^.]*$|$)", path)
    if match:
        return match.group(1)


def replace_imports(files):
    # create a dictionary mapping filenames to file contents
    file_dict = {filename: content for filename, content in files}

    # helper function to recursively replace imports in a file
    def replace_import(content):
        # find all the import statements in the file
        import_statements = re.findall(r"\\input\{(.*?)\}", content)

        # for each import statement, replace it with the content of the imported file
        for import_filename in import_statements:
            print("Replaceing file input", import_filename)
            if import_filename in file_dict:
                imported_content = replace_import(file_dict[import_filename])
                content = content.replace(
                    f"\\input{{{import_filename}}}", imported_content
                )

        return content

    # replace imports in all files
    for i in range(len(files)):
        filename, content = files[i]
        files[i] = [filename, replace_import(content)]

    return files
