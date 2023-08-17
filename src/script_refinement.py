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


def generate_script(barebone_script_json: dict):
    """
    Given the summary of the paper, generate a detailed video script.
    This function queries the chroma vector database for each section to generate a script for a video.
    """

    # Load json and iterate over each section
    sections = barebone_script_json["sections"]

    for section in sections:
        title = section["title"]

        section_script = query_chroma_by_prompt_with_template(title)

        # Remove the special characters
        section_script = section_script.replace("\n", " ").replace("\\", "")

        # Write the script back to the section in the dictionary
        section["script"] = section_script

        # Sleep for 10 seconds between requests
        time.sleep(10)

    return barebone_script_json


def enrich_script_with_resources(section_script: list):
    enriched_scripts = []

    for script in section_script:
        # For simplicity, let's assume chroma also has access to relevant resources.
        resource_prompt = f"Based on the content:\n\n{script}\n\nCan you suggest visual resources or cues to enhance this section for a video presentation?"
        suggested_resources = query_chroma_by_prompt(resource_prompt)

        enriched_section = {"script": script, "resources": suggested_resources}

        enriched_scripts.append(enriched_section)
        time.sleep(15)  # Sleep for 15 seconds between requests

    return enriched_scripts


def generate_script_scenes(section: ScriptSection, last_two_sections: tuple[str, str]):
    """
    Given the script of a section, generate a list of scenes for the video.
    """

    docs = query_chroma_by_prompt(section["title"])
    print(docs)

    prompt_template = textwrap.dedent(
    """
    ---INSTRUCTIONS---
    Using the provided section context and related document snippets, design engaging video scenes. Adhere to these specifications:

    - Generate a minimum of 4 unique scenes from the section context.
    - For each scene:
        * Produce a `SpeakerScript`: A concise statement for video narration. Exclude references like "the paper mentions" or "according to the author."
        * Formulate a `StockFootageQuery`: Specific search terms for platforms such as Pixabay. For abstract topics, use clear, non-ambiguous descriptors.
        * Note: Set the scene type to TEXT.
    - Ensure varied `StockFootageQuery` across all scenes.
    - Align narration with the paper author's style.
    - Aim for viewer engagement while maintaining factual accuracy. Address a non-scientific audience, avoiding jargon, abstract examples and repetition.

    ---PREVIOUS SECTIONS (For Reference)---
    {last_two_sections}

    ---SECTION CONTEXT---
    {section_context}

    ---DOCUMENT SNIPPETS---
    {relevant_docs}
    """
    )

    prompt_template = PromptTemplate.from_template(template=prompt_template)

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

    prompt_template = textwrap.dedent(
    """
    ---INSTRUCTIONS---
    Given the provided script for a YouTube video narration about a scientific paper, refine each scene's 'speakerScript' and 'stockFootageQuery' to increase clarity, engagement, and accessibility for a general audience. The overarching narrative should maintain a coherent and fluid storyline, ensuring viewers can easily follow the content.

    For each scene, ensure the following:

    1. The 'speakerScript' should:
    - Start with a warm welcome to the audience for the first scene.
    - Conclude with a thank you and an invitation to the next video for the last scene.
    - Be concise and clear, avoiding unnecessary technical jargon.
    - Use relatable analogies or examples where necessary.
    - Maintain a logical flow, ensuring the content follows a red thread throughout.

    2. The 'stockFootageQuery' should:
    - Be general enough to fetch a broad range of relevant results.
    - Relate closely to the scene's core message.
    - Avoid highly technical terms or niche references.

    Provide a refined script maintaining the original structure, ensuring it's tailored for a YouTube audience.

    ---ORIGINAL SCRIPT---
    {script_data}
    """
    )

    prompt_template = PromptTemplate.from_template(template=prompt_template)

    llm = ChatOpenAI(model_name="gpt-4", temperature=0.75)

    answer_obj = answer_as_json(
        llm=llm,
        schema=script_schema,
        prompt=prompt_template,
        input=({'script_data': script_json}),
    )

    return answer_obj["scenes"]
