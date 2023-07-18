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

from tmp import tmp_archive_path, tmp_dir_path, tmp_latex_path, tmp_res_path

def arxiv_id_to_latex(paper_id: str) -> str:
    """Example id: 1706.03762"""
    
    dir_path = tmp_dir_path(paper_id)
    archive_path = tmp_archive_path(paper_id)
    res_path = tmp_res_path(paper_id)
    latex_path = tmp_latex_path(paper_id)

    if os.path.exists(latex_path):
        logging.info("Already downloaded this paper, returning cached version.")
        return read_file(latex_path)

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

    with open(latex_path, "w") as f:
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
        tex_contents.append([get_filename(file_path), read_file(file_path)])

    tex_contents = order_by_input_occurrences(tex_contents)

    tex_files_content = replace_imports(tex_contents)

    return tex_files_content[0][1]
    
    
def order_by_input_occurrences(arr: List[List[str]]) -> List[List[str]]:
    return sorted(arr, key=lambda x: x[1].count('\\input'), reverse=True)

def get_filename(path: str) -> str:
    match = re.search(r'\/?([^/]*?)(?=\.[^.]*$|$)', path)
    if match:
        return match.group(1)


def replace_imports(files):
    # create a dictionary mapping filenames to file contents
    file_dict = {filename: content for filename, content in files}

    # helper function to recursively replace imports in a file
    def replace_import(content):
        # find all the import statements in the file
        import_statements = re.findall(r'\\input\{(.*?)\}', content)

        # for each import statement, replace it with the content of the imported file
        for import_filename in import_statements:
            print("Replaceing file input", import_filename)
            if import_filename in file_dict:
                imported_content = replace_import(file_dict[import_filename])
                content = content.replace(f'\\input{{{import_filename}}}', imported_content)

        return content

    # replace imports in all files
    for i in range(len(files)):
        filename, content = files[i]
        files[i] = [filename, replace_import(content)]

    return files