from concurrent.futures import ThreadPoolExecutor
import multiprocessing
import os
import logging
from dotenv import load_dotenv

from .progress_handler import update_progress
from .fetch_google_image import fetch_google_images
from .paper_loader import paper_id_to_latex
from .chroma import vectorize_latex_in_chroma
from .langchain_summarize import (
    COMBINE_SUMMARY_PROMPT,
    MAP_SUMMARY_PROMPT,
    summarize_by_map_reduce,
)
from .summary_to_script import generate_barebone_script
from .script_refinement import generate_script_scenes, refine_script_content
from .text_to_voice import generate_script_audio_pieces
from .stock_footage import generate_stock_footage
from .text_alignments_to_captions import generate_video_captions
from .vid_render import render_vid
from .tmp import tmp_loader, tmp_path, tmp_saver
import sys

# Configure logging
load_dotenv()


def fetch_paper(paper_id):
    logging.info(f"Fetching paper with id {paper_id}")
    return paper_id_to_latex(paper_id)


def vectorize_paper(paper_id, latex):
    logging.info(f"Vectorizing paper")
    vectorize_latex_in_chroma(paper_id, latex)


def get_summary(paper_id, latex):
    summary = tmp_loader(paper_id=paper_id, kind="summary", save_type="str")
    if summary is None:
        logging.info(f"Generating summary")
        summary = summarize_by_map_reduce(
            latex, MAP_SUMMARY_PROMPT, COMBINE_SUMMARY_PROMPT
        )
        tmp_saver(paper_id=paper_id, kind="summary", data=summary, save_type="str")
    else:
        logging.info("Using cached summary")
    return summary


def generate_script_from_summary(paper_id, summary):
    barebone_script_json = tmp_loader(
        paper_id=paper_id, kind="barebone_script", save_type="json"
    )
    if barebone_script_json is None:
        logging.info(f"Generating barebone video script")
        barebone_script_json = generate_barebone_script(summary)
        tmp_saver(
            paper_id=paper_id,
            kind="barebone_script",
            data=barebone_script_json,
            save_type="json",
        )
    else:
        logging.info("Using cached barebone script")
    return barebone_script_json


def enrich_script(paper_id, barebone_script_json):
    script_with_scenes = tmp_loader(
        paper_id=paper_id, kind="script_with_scenes", save_type="json"
    )
    if script_with_scenes is None:
        logging.info(f"Generating detailed context for each section")
        script_with_scenes = {"sections": []}
        sections = barebone_script_json["sections"]

        for index, section in enumerate(sections):
            # Determine the last two sections
            if index == 0:
                last_two = []
            elif index == 1:
                last_two = [sections[index - 1]["context"]]
            else:
                last_two = [
                    sections[index - 2]["context"],
                    sections[index - 1]["context"],
                ]

            scenes = generate_script_scenes(
                paper_id, section, last_two_sections=last_two
            )

            # Append section and its scenes to the script_with_scenes
            script_with_scenes["sections"].append(section)
            script_with_scenes["sections"][-1]["scenes"] = scenes

        tmp_saver(
            paper_id=paper_id,
            kind="script_with_scenes",
            data=script_with_scenes,
            save_type="json",
        )
    else:
        logging.info("Using cached enriched script")

    return script_with_scenes


def refine_script(paper_id: str):
    refined_script = tmp_loader(
        paper_id=paper_id, kind="script_with_scenes_refined", save_type="json"
    )

    if refined_script is None:
        logging.info(f"Refine script...")

        script_with_scenes = tmp_loader(
            paper_id=paper_id, kind="script_with_scenes", save_type="json"
        )
        if not script_with_scenes:
            raise ValueError("Script not found.")

        refined_script = refine_script_content(script_with_scenes)

        tmp_saver(
            paper_id=paper_id,
            kind="script_with_scenes_refined",
            data=refined_script,
            save_type="json",
        )
    else:
        logging.info("Using cached refined script")

    return refined_script


def generate_audio(paper_id, script_with_scenes):
    logging.info(f"Generating script audio pieces")
    return generate_script_audio_pieces(paper_id=paper_id, script=script_with_scenes)


def get_stock_footage(paper_id, script_with_scenes):
    logging.info(f"Generating stock footage")
    return generate_stock_footage(paper_id=paper_id, script=script_with_scenes)


def generate_captions(paper_id, script_with_scenes):
    logging.info(f"Generating video captions")
    return generate_video_captions(paper_id=paper_id, script=script_with_scenes)


def render_video(paper_id, refined_script) -> str:
    logging.info(f"Generating video")
    render_vid(
        paper_id,
        refined_script,
        output_filename=tmp_path(paper_id=paper_id, kind="output"),
    )

    return paper_id


def paper_2_video(paper_id):
    try:
        # Step 1
        update_progress(paper_id, 1, 6)
        latex = fetch_paper(paper_id)
        vectorize_paper(paper_id, latex)

        # Step 2
        update_progress(paper_id, 2, 6)
        summary = get_summary(paper_id, latex)

        # Step 3
        update_progress(paper_id, 3, 6)
        barebone_script = generate_script_from_summary(paper_id, summary)

        # Step 4
        update_progress(paper_id, 4, 6)
        enriched_script = enrich_script(paper_id, barebone_script)

        # Step 5
        update_progress(paper_id, 5, 6)
        cpu_cores = multiprocessing.cpu_count()
        with ThreadPoolExecutor(max_workers=cpu_cores) as executor:
            executor.submit(generate_audio, paper_id, enriched_script)
            executor.submit(get_stock_footage, paper_id, enriched_script)
            executor.submit(
                fetch_google_images, paper_id=paper_id, script=enriched_script
            )
            executor.submit(generate_captions, paper_id, enriched_script)

        # Step 6
        update_progress(paper_id, 6, 6)
        video_file_id = render_video(paper_id, enriched_script)

        return video_file_id

    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    logging.info("Starting pipeline...")
    paper_id = sys.argv[1] if len(sys.argv) > 1 else "2303.12712"
    paper_2_video(paper_id)
