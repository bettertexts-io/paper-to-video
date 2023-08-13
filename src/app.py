import json
import os
import sys

from dotenv import load_dotenv

from chroma import vectorize_latex_in_chroma
from constants import MOCK_SUMMARY
from langchain_summarize import (
    COMBINE_SUMMARY_PROMPT,
    CRAFT_SCRIPT_PROMPT,
    MAP_SUMMARY_PROMPT,
    summarize_by_map_reduce,
    summarize_by_refine,
)
from paper_loader import paper_id_to_latex
from script_refinement import generate_script, generate_script_scenes
from stock_footage import generate_stock_footage
from summary_to_script import generate_barebone_script
from text_alignments_to_captions import  generate_video_captions
from text_to_voice import generate_script_audio_pieces, text_to_voice
from tmp import tmp_loader, tmp_path, tmp_saver
from vid_render import render_vid

load_dotenv()


SKIP_VECTORIZATION = True


def paper_2_video(paper_id, MOCK_SUMMARY=None):
    try:
        print(f"Fetching paper with id {paper_id}")
        latex = paper_id_to_latex(paper_id)
    except Exception as e:
        print(f"Failed to fetch the paper with id {paper_id}: {e}")
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
        summary = tmp_loader(paper_id=paper_id, kind="summary", save_type="str")

        if summary is None:
            print(f"Generating summary")
            summary = summarize_by_map_reduce(latex, MAP_SUMMARY_PROMPT, COMBINE_SUMMARY_PROMPT)
            tmp_saver(paper_id=paper_id, kind="summary", data=summary, save_type="str")
        else:
            print("Using cached summary")

    except Exception as e:
        print(f"Failed to summarize the paper: {e}")
        return

    try:
        # Check the path for the barebone script

        barebone_script_json = tmp_loader(
            paper_id=paper_id, kind="barebone_script", save_type="json"
        )

        if barebone_script_json is None:
            print(f"Generating barebone video script")
            # Turn the summary into a barebone video script structure with approximated lengths of the sections
            barebone_script_json = generate_barebone_script(summary)
            tmp_saver(
                paper_id=paper_id,
                kind="barebone_script",
                data=barebone_script_json,
                save_type="json",
            )
        else:
            print("Using cached barebone script")

    except Exception as e:
        print(f"Failed to create video script: {e}")

    try:
        # Define the path for the enriched script
        script_with_scenes = tmp_loader(
            paper_id=paper_id, kind="script_with_scenes", save_type="json"
        )

        # Otherwise, generate the enriched script and store it
        if script_with_scenes is None:
            print(f"Generating detailed context for each section")
            # Generate a detailed summary for each section of the generated script structure
            # Feed in the generated barebone script
            # enriched_script_json = generate_script(barebone_script_json)
            script_with_scenes = {"sections": []}
            for section in barebone_script_json["sections"]:
                print(section)
                scenes = generate_script_scenes(section)
                script_with_scenes["sections"].append(section)
                script_with_scenes["sections"][-1]["scenes"] = scenes

            print(script_with_scenes)
            tmp_saver(
                paper_id=paper_id,
                kind="script_with_scenes",
                data=script_with_scenes,
                save_type="json",
            )
        else:
            print("Using cached enriched script")

    except Exception as e:
        print(f"Failed to generate detailed summary: {e}")
        return

    try:
        # Convert script into audio pieces
        print(f"Generating script audio pieces")
        audio_paths = generate_script_audio_pieces(
            paper_id=paper_id, script=script_with_scenes
        )

    except Exception as e:
        print(f"Failed to generate audio pieces: {e}")
        return
    
    try: 
        stock_footage_paths = generate_stock_footage(paper_id=paper_id, script=script_with_scenes)
    except Exception as e:
        print(f"Failed to generate stock footage: {e}")
        return
    
    try: 
        print(f"Generating video captions")
        video_caption_filenames = generate_video_captions(paper_id=paper_id, script=script_with_scenes)
    except Exception as e:
        print(f"Failed to generate video captions: {e}")
        return

    try:
        # Convert audio pieces into video
        print(f"Generating video")
        render_vid(
            animation_filenames=stock_footage_paths,
            voice_filenames=audio_paths,
            video_caption_filenames=video_caption_filenames,
            output_filename=tmp_path(paper_id=paper_id, kind="output"),
        )
    except Exception as e:
        print(f"Failed to create video: {e}")
        return


if __name__ == "__main__":
    print("Starting app")
    paper_2_video("1706.03762", MOCK_SUMMARY=MOCK_SUMMARY)
