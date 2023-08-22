import logging
import textwrap
import time
import re

from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI

from answer_as_json import answer_as_json
from chroma import (
    query_chroma,
    query_chroma_by_prompt,
    query_chroma_by_prompt_with_template,
)
from script import ScriptSection, script_scene_schema, script_schema


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


def generate_script_scenes(paper_id: str, section: ScriptSection, last_two_sections: tuple[str, str]):
    """
    Given the script of a section, generate a list of scenes for the video.
    """

    docs = query_chroma_by_prompt(paper_id, section["title"])

    prompt_input = textwrap.dedent(
    """
    ---INSTRUCTIONS---
    You are to craft engaging video scenes inspired by the style of Yannic Kilcher, known for his deep dives into academic papers. Follow these guidelines:

    - Generate at least 4 unique scenes derived from the section context.
    - For each scene:
        * Create a `SpeakerScript`: Frame your narration as if you're taking the viewer on a detailed academic journey. Intermingle explanations with questions, comparisons, and relevant challenges. Avoid saying "the paper mentions" or "according to the author."
        * Construct a `StockFootageQuery`: Search terms suitable for platforms like Pixabay. For abstract topics, opt for direct, non-ambiguous terms.
        * Note: Set the scene type to TEXT.
    - Diversify the `StockFootageQuery` for each scene.
    - Channel the engaging, detail-oriented approach of Yannic Kilcher. 
    - Strive for viewer engagement, preserving factual precision. Tailor the content for an academic audience, steering clear of vague examples and redundancy.

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
        input=({'section_context': section["context"], 'relevant_docs': str(docs), 'last_two_sections': last_two_sections}),
    )

    return answer_obj["scenes"]


def refine_script_content(script_json: str):
    """
    Given the script, refine the speakerScript and the stockFootageQuery
    """

    text_template = textwrap.dedent(
    """
    ---INSTRUCTIONS---
    We're on a mission to create an engaging YouTube video about a scientific paper. Using the script provided, refine its narrative for an academic YouTube audience. We want our viewers to have a smooth journey from the first scene to the last.

    Follow these steps for each scene:

    1. 'SpeakerScript' refinements:
    - Begin the first scene with a friendly welcome to our audience.
    - Wind up the last scene with gratitude and a teaser for the next video.
    - Keep it short and sweet, skipping over heavy jargon.
    - When complex topics pop up, bridge the gap with relatable examples or analogies.
    - Craft a storyline that has a clear beginning, middle, and end, weaving a red thread throughout.

    2. 'StockFootageQuery' suggestions:
    - Choose terms that offer a rich pool of relevant visuals.
    - Ensure the visuals underscore the core message of the scene.

    Please retain the original script's structure, refining its essence for enhanced clarity, engagement, and viewer retention.

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
        input=({'script_data': script_json}),
    )

    return answer_obj
