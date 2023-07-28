import os
import json
import logging
from chroma import vectorize_latex_in_chroma
from constants import MOCK_SUMMARY
from langchain_summarize import CRAFT_SCRIPT_PROMPT, LATEX_SUMMARY_WITH_SECTIONS_PROMPT, summarize_by_map_reduce, summarize_by_refine
from paper_loader import arxiv_id_to_latex
from summary_to_script import generate_barebone_script
from script_refinement import generate_script
from text_to_voice import text_to_voice
from elevenlabs import play
from tmp import tmp_barebone_script_path, tmp_script_path

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
        # Check the path for the barebone script
        barebone_path = tmp_barebone_script_path(arxiv_id)
        
        # If the file already exists, load it
        if os.path.exists(barebone_path):
            with open(barebone_path, 'r') as f:
                barebone_script_json = json.load(f)
        # Otherwise, generate the barebone script and store it
        else:
            # Turn the summary into a barebone video script structure with approximated lengths of the sections
            barebone_script_json = generate_barebone_script(summary)

            # Store barebone script in tmp folder
            with open(barebone_path, 'w') as f:
                json.dump(barebone_script_json, f, indent=4)
            
    except Exception as e:
        logging.error(f"Failed to create video script: {e}")
        return
    
    try:
        # Define the path for the enriched script
        script_path = tmp_script_path(arxiv_id)

        # If the file already exists, load it
        if os.path.exists(script_path):
            with open(script_path, 'r') as f:
                enriched_script_json = json.load(f)
        # Otherwise, generate the enriched script and store it
        else:
            # Generate a detailed summary for each section of the generated script structure
            # Feed in the generated barebone script
            enriched_script_json = generate_script(barebone_script_json)
            
            # Store script in tmp folder
            with open(script_path, 'w') as f:
                json.dump(enriched_script_json, f, indent=4)
    except Exception as e:
        logging.error(f"Failed to generate detailed summary: {e}")
        return

    try:
        # TODO: Generate scene resources using manim
        print()
    except Exception as e:
        logging.error(f"Failed to convert text to speech: {e}")
        return

    try:
        sections = enriched_script_json["sections"]
        script = ""
        for section in sections:
            section_script = section["script"]
            script += section_script
        
        # Convert section scripts into one script
        final_script = summarize_by_refine(script, CRAFT_SCRIPT_PROMPT)
        print(final_script)
    except Exception as e:
        logging.error(f"Failed to create video: {e}")
        return
    

    try:
        # Convert script into audio
        # TODO: First chunk final script by 5000 chars
        print()
    except Exception as e:
        logging.error(f"Failed to create video: {e}")
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
