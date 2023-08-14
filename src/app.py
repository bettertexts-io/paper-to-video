import os
import logging
from dotenv import load_dotenv
from paper_loader import paper_id_to_latex
from chroma import vectorize_latex_in_chroma
from langchain_summarize import (
    COMBINE_SUMMARY_PROMPT,
    MAP_SUMMARY_PROMPT,
    summarize_by_map_reduce,
)
from summary_to_script import generate_barebone_script
from script_refinement import generate_script_scenes
from text_to_voice import generate_script_audio_pieces
from stock_footage import generate_stock_footage
from text_alignments_to_captions import generate_video_captions
from vid_render import render_vid
from tmp import tmp_loader, tmp_path, tmp_saver

# Configure logging
logging.basicConfig(level=logging.INFO)
load_dotenv()

SKIP_VECTORIZATION = True

def fetch_paper(paper_id):
    logging.info(f"Fetching paper with id {paper_id}")
    return paper_id_to_latex(paper_id)

def vectorize_paper(latex):
    if not SKIP_VECTORIZATION:
        logging.info(f"Vectorizing paper")
        vectorize_latex_in_chroma(latex)

def get_summary(paper_id, latex):
    summary = tmp_loader(paper_id=paper_id, kind="summary", save_type="str")
    if summary is None:
        logging.info(f"Generating summary")
        summary = summarize_by_map_reduce(latex, MAP_SUMMARY_PROMPT, COMBINE_SUMMARY_PROMPT)
        tmp_saver(paper_id=paper_id, kind="summary", data=summary, save_type="str")
    else:
        logging.info("Using cached summary")
    return summary

def generate_script_from_summary(paper_id, summary):
    barebone_script_json = tmp_loader(paper_id=paper_id, kind="barebone_script", save_type="json")
    if barebone_script_json is None:
        logging.info(f"Generating barebone video script")
        barebone_script_json = generate_barebone_script(summary)
        tmp_saver(paper_id=paper_id, kind="barebone_script", data=barebone_script_json, save_type="json")
    else:
        logging.info("Using cached barebone script")
    return barebone_script_json

def enrich_script(paper_id, barebone_script_json):
    script_with_scenes = tmp_loader(paper_id=paper_id, kind="script_with_scenes", save_type="json")
    if script_with_scenes is None:
        logging.info(f"Generating detailed context for each section")
        script_with_scenes = {"sections": []}
        for section in barebone_script_json["sections"]:
            scenes = generate_script_scenes(section)
            script_with_scenes["sections"].append(section)
            script_with_scenes["sections"][-1]["scenes"] = scenes
        tmp_saver(paper_id=paper_id, kind="script_with_scenes", data=script_with_scenes, save_type="json")
    else:
        logging.info("Using cached enriched script")
    return script_with_scenes

def generate_audio(paper_id, script_with_scenes):
    logging.info(f"Generating script audio pieces")
    return generate_script_audio_pieces(paper_id=paper_id, script=script_with_scenes)

def get_stock_footage(paper_id, script_with_scenes):
    logging.info(f"Generating stock footage")
    return generate_stock_footage(paper_id=paper_id, script=script_with_scenes)

def generate_captions(paper_id, script_with_scenes):
    logging.info(f"Generating video captions")
    return generate_video_captions(paper_id=paper_id, script=script_with_scenes)

def render_video(stock_footage_paths, audio_paths, video_caption_filenames, paper_id):
    logging.info(f"Generating video")
    render_vid(
        animation_filenames=stock_footage_paths,
        voice_filenames=audio_paths,
        video_caption_filenames=video_caption_filenames,
        output_filename=tmp_path(paper_id=paper_id, kind="output"),
    )

def paper_2_video(paper_id):
    try:
        latex = fetch_paper(paper_id)
        vectorize_paper(latex)
        summary = get_summary(paper_id, latex)
        barebone_script = generate_script_from_summary(paper_id, summary)
        enriched_script = enrich_script(paper_id, barebone_script)
        audio_pieces = generate_audio(paper_id, enriched_script)
        stock_footage_paths = get_stock_footage(paper_id, enriched_script)
        captions = generate_captions(paper_id, enriched_script)
        render_video(stock_footage_paths, audio_pieces, captions, paper_id)
    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    logging.info("Starting pipeline...")
    paper_2_video("1706.03762")
