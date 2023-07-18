def tmp_dir_path(paper_id):
    return f"tmp/{paper_id}"

def tmp_archive_path(paper_id):
    return f"{tmp_dir_path(paper_id)}/arch.gz"

def tmp_res_path(paper_id):
    return f"{tmp_dir_path(paper_id)}/res"

def tmp_latex_path(paper_id):
    return f"{tmp_dir_path(paper_id)}/latex.tex"

def tmp_barebone_script_path(paper_id):
    return f"{tmp_dir_path(paper_id)}/barebone.json"