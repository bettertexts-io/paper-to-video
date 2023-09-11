import logging
import textwrap
import time
import re

from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI

from .answer_as_json import answer_as_json
from .chroma import (
    query_chroma,
    query_chroma_by_prompt,
    query_chroma_by_prompt_with_template,
)
from .script import ScriptSection, script_scene_schema, script_schema


def generate_script(paper_id: str, barebone_script_json: dict):
    """
    Given the summary of the paper, generate a detailed video script.
    This function queries the chroma vector database for each section to generate a script for a video.
    """

    # Load json and iterate over each section
    sections = barebone_script_json["sections"]

    for section in sections:
        title = section["title"]

        section_script = query_chroma_by_prompt_with_template(paper_id, title)

        # Remove the special characters
        section_script = section_script.replace("\n", " ").replace("\\", "")

        # Write the script back to the section in the dictionary
        section["script"] = section_script

        # Sleep for 10 seconds between requests
        time.sleep(10)

    return barebone_script_json


def enrich_script_with_resources(paper_id: str, section_script: list):
    enriched_scripts = []

    for script in section_script:
        # For simplicity, let's assume chroma also has access to relevant resources.
        resource_prompt = f"Based on the content:\n\n{script}\n\nCan you suggest visual resources or cues to enhance this section for a video presentation?"
        suggested_resources = query_chroma_by_prompt(paper_id, resource_prompt)

        enriched_section = {"script": script, "resources": suggested_resources}

        enriched_scripts.append(enriched_section)
        time.sleep(15)  # Sleep for 15 seconds between requests

    return enriched_scripts


def generate_script_scenes(
    paper_id: str, section: ScriptSection, last_two_sections: tuple[str, str]
):
    """
    Given the script of a section, generate a list of scenes for the video.
    """

    docs = query_chroma_by_prompt(paper_id, section["title"])

    prompt_input = textwrap.dedent(
        """
    ---INSTRUCTIONS---
    Your task is to design insightful video scenes reminiscent of Yannic Kilcher's in-depth explorations of academic topics. Ensure the following:

    - Derive a minimum of 4 unique scenes from the provided section context.
    - For each scene:
        * `SpeakerScript`: Guide the viewer through a rigorous yet engaging academic discourse. Weave the narrative with clarifying explanations, posed queries, relevant contrasts, and technical challenges. Avoid directly referencing the original paper or its authors. 
        * `StockFootageQuery`: Choose search terms apt for stock platforms like Pixabay. For theoretical concepts, employ clear and specific terminology to capture the essence.
        * Note: Always set the scene type to TEXT.
    - Ensure diversity in the `StockFootageQuery` across scenes.
    - Emulate the meticulous, depth-driven approach characteristic of Yannic Kilcher.
    - Prioritize factual accuracy while keeping the academic audience engrossed. Sidestep overly broad examples and repetitiveness.

    ---PREVIOUS SECTIONS (For Reference)---
    {last_two_sections}

    ---SECTION CONTEXT---
    {section_context}

    ---DOCUMENT SNIPPETS---
    {relevant_docs}
    """
    )

    prompt_template = PromptTemplate.from_template(template=prompt_input)

    llm = ChatOpenAI(model_name="gpt-4", temperature=0.7)

    answer_obj = answer_as_json(
        llm=llm,
        schema=script_scene_schema,
        prompt=prompt_template,
        input=(
            {
                "section_context": section["context"],
                "relevant_docs": str(docs),
                "last_two_sections": last_two_sections,
            }
        ),
    )

    return answer_obj["scenes"]


def refine_script_content(script_json: str):
    """
    Given the script, refine the speakerScript and the stockFootageQuery
    """

    text_template = textwrap.dedent(
        """
    ---INSTRUCTIONS---
    We're diving deep into a scientific exploration in the style of Yannic Kilcher. The goal is to create an engaging YouTube video inspired by a particular academic theme, and we need to ensure it's crystal clear and captivating for our audience.

    When refining each scene in the provided script, kindly adhere to the following steps:

    1. 'SpeakerScript' refinements:
    - Begin with an enthusiastic welcome, drawing our viewers into the academic journey right from the first scene.
    - Conclude the last scene with gratitude, subtly hinting at the excitement the next video promises.
    - Weave a consistent storyline throughout, ensuring there's a coherent narrative arc from start to finish.

    2. 'StockFootageQuery' suggestions:
    - Handpick terms that will lead to visuals deeply aligned with the scene's core message. The more relevant, the better.

    Please stay true to the essence of the original script. What we're aiming for is enhanced clarity, viewer immersion, and continuity.

    ---ORIGINAL SCRIPT---
    {script_data}
    """
    )

    prompt_template = PromptTemplate.from_template(template=text_template)

    llm = ChatOpenAI(model_name="gpt-4", temperature=0.75)

    answer_obj = answer_as_json(
        llm=llm,
        schema=script_schema,
        prompt=prompt_template,
        input=({"script_data": script_json}),
    )

    return answer_obj
