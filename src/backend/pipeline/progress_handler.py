progress_dict = {}


def update_progress(paper_id, step, total_steps):
    progress_percentage = (step / total_steps) * 100
    progress_dict[paper_id] = {"progress": progress_percentage}
