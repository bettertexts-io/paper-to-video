progress_dict = {}


def update_progress(paper_id, step, total_steps):
    progress_dict[paper_id] = (step, total_steps)
