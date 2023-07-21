import json
import logging
from chroma import vectorize_latex_in_chroma
from constants import MOCK_SUMMARY
from langchain_summarize import LATEX_SUMMARY_WITH_SECTIONS_PROMPT, summarize_by_map_reduce
from paper_loader import arxiv_id_to_latex
from summary_to_script import generate_barebone_script
from script_refinement import generate_script
from tmp import tmp_barebone_script_path

logging.basicConfig(level=logging.INFO)

SKIP_VECTORIZATION = True

def paper_2_video(arxiv_id, MOCK_SUMMARY=None):
    
    try:
        latex = arxiv_id_to_latex(arxiv_id)
    except Exception as e:
        logging.error(f"Failed to fetch the paper with id {arxiv_id}: {e}")
        return
    
    try:
        # Check if paper is already vectorized otherwise store vectors in chroma db
        if not SKIP_VECTORIZATION:
            vectorize_latex_in_chroma(latex)
    except Exception as e:
        logging.error(f"Failed to vectorize paper")
        return

    try:
        # Summarize the paper using langchain map_reduce summarization
        # The summary includes a list of the sections of the paper at the end
        if MOCK_SUMMARY:
            summary = MOCK_SUMMARY
        else:
            summary = summarize_by_map_reduce(latex, LATEX_SUMMARY_WITH_SECTIONS_PROMPT)
    except Exception as e:
        logging.error(f"Failed to summarize the paper: {e}")
        return

    try:
        # Turn the summary into a barebone video script structure with approximated lengths of the sections
        barebone_script_json = generate_barebone_script(summary)

        print(barebone_script_json)

        # Store barebone script in tmp folder
        barebone_path = tmp_barebone_script_path(arxiv_id)
        with open(barebone_path, 'w') as f:
            json.dump(barebone_script_json, f, indent=4)
            
    except Exception as e:
        logging.error(f"Failed to create video script: {e}")
        return
    
    try:
        # Generate a detailed summary for each section of the generated script structure
        # Feed in the generated barebone script
        section_script = generate_script(barebone_script_json)
        print(section_script)
    except Exception as e:
        logging.error(f"Failed to generate detailed summary: {e}")
        return

    try:
        # TODO: Generate a detailed script snipped with resources for each section of the generated script structure
        # Feed in the generated focussed summaries for each section
        print()
    except Exception as e:
        logging.error(f"Failed to convert text to speech: {e}")
        return

    try:
        # TODO: Render the script into a video
        print()
    except Exception as e:
        logging.error(f"Failed to create video: {e}")
        return

    logging.info(f"Successfully created video for paper {arxiv_id}")


if __name__ == "__main__":    
    paper_2_video("1706.03762", MOCK_SUMMARY=MOCK_SUMMARY)
