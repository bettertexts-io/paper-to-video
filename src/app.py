import os
import json
import sys
from chroma import vectorize_latex_in_chroma
from constants import MOCK_SUMMARY
from langchain_summarize import CRAFT_SCRIPT_PROMPT, LATEX_SUMMARY_WITH_SECTIONS_PROMPT, summarize_by_map_reduce, summarize_by_refine
from paper_loader import arxiv_id_to_latex
from summary_to_script import generate_barebone_script
from script_refinement import generate_script, generate_script_scenes
from text_to_voice import text_to_voice
from dotenv import load_dotenv

from tmp import tmp_loader, tmp_saver
load_dotenv()


SKIP_VECTORIZATION = True

def paper_2_video(arxiv_id, MOCK_SUMMARY=None):
    try:
        print(f"Fetching paper with id {arxiv_id}")
        latex = arxiv_id_to_latex(arxiv_id)
    except Exception as e:
        print(f"Failed to fetch the paper with id {arxiv_id}: {e}")
        return
    
    try:
        # Check if paper is already vectorized otherwise store vectors in chroma db
        print(f"Vectorizing paper")
        if not SKIP_VECTORIZATION:
            vectorize_latex_in_chroma(latex)
    except Exception as e:
        print(f"Failed to vectorize paper")
        return
    
    try:
        # Summarize the paper using langchain map_reduce summarization
        # The summary includes a list of the sections of the paper at the end
        summary = tmp_loader(paper_id=arxiv_id, kind="summary", save_type="str")

        if summary is None:
            print(f"Generating summary")
            summary = summarize_by_map_reduce(latex, LATEX_SUMMARY_WITH_SECTIONS_PROMPT)
            tmp_saver(paper_id=arxiv_id, kind="summary", data=summary, save_type="str")
        else:
            print("Using cached summary")

    except Exception as e:
        print(f"Failed to summarize the paper: {e}")
        return

    try:
        # Check the path for the barebone script

        barebone_script_json = tmp_loader(paper_id=arxiv_id, kind="barebone_script", save_type="json")

        if barebone_script_json is None:
            print(f"Generating barebone video script")
            # Turn the summary into a barebone video script structure with approximated lengths of the sections
            barebone_script_json = generate_barebone_script(summary)
            tmp_saver(paper_id=arxiv_id, kind="barebone_script", data=barebone_script_json, save_type="json")
        else: 
            print("Using cached barebone script")
            
    except Exception as e:
        print(f"Failed to create video script: {e}")
        return
    
    try:
        # Define the path for the enriched script
        


        script_with_scenes = tmp_loader(paper_id=arxiv_id, kind="script_with_scenes", save_type="json")

        # Otherwise, generate the enriched script and store it
        if script_with_scenes is None:
            print(f"Generating detailed context for each section")
            # Generate a detailed summary for each section of the generated script structure
            # Feed in the generated barebone script
            # enriched_script_json = generate_script(barebone_script_json)
            script_with_scenes = {
                "sections": []
            }
            for section in barebone_script_json["sections"]:
                print(section)
                scenes = generate_script_scenes(section)
                script_with_scenes["sections"].append(section)
                script_with_scenes["sections"][-1]["scenes"] = scenes
                
            print(script_with_scenes)
            tmp_saver(paper_id=arxiv_id, kind="script_with_scenes", data=script_with_scenes, save_type="json")
        else:
            print("Using cached enriched script")

            


    except Exception as e:
        print(f"Failed to generate detailed summary: {e}")
        return

    return


    try:
        # TODO: Generate scene resources using manim
        print()
    except Exception as e:
        print(f"Failed to convert text to speech: {e}")
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
        print(f"Failed to create video: {e}")
        return
    

    try:
        # Convert script into audio
        # TODO: First chunk final script by 5000 chars
        print()
    except Exception as e:
        print(f"Failed to create video: {e}")
        return

    try:
        # TODO: Render the script into a video
        print()
    except Exception as e:
        print(f"Failed to create video: {e}")
        return

    print(f"Successfully created video for paper {arxiv_id}")


if __name__ == "__main__":    
    print("Starting app")
    paper_2_video("1706.03762", MOCK_SUMMARY=MOCK_SUMMARY)
