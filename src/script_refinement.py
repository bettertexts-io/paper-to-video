import logging
import textwrap
import time

from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI

from answer_as_json import answer_as_json
from chroma import (
    query_chroma,
    query_chroma_by_prompt,
    query_chroma_by_prompt_with_template,
)
from script import ScriptSection, script_scene_schema


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


def generate_script_scenes(section: ScriptSection):
    """
    Given the script of a section, generate a list of scenes for the video.
    """

    scenes = []

    docs = query_chroma_by_prompt(section["title"])
    print(docs)

    text_template = textwrap.dedent(
        """
        ---INSTRUCTIONS---
        You are tasked to create video scenes based on a given section description and context documents, following these specific guidelines:

        - Divide the section context into at least 5 distinct scenes.
        - Use the section context's content to structure the scenes, with each scene having attributes to generate voice, image, and caption components.
        - Prepare a precise speakerScript for each scene, as this will be used to create the voice component of the video.
        - For each scene, use a stockFootageQuery to select exactly one stock image resource.
        - All scenes must be of the type TEXT.
        - Craft the narration in the voice of the paper's author, excluding indirect references such as "the paper says" or "the author says."
        - Optimize the scenes for viewer engagement, maintaining the factual accuracy of the content.

        ---Section context---
        {section_context}

        ---Relevant document snippets---
        {relevant_docs}
    """
    )

    prompt_template = PromptTemplate.from_template(template=text_template)

    llm = ChatOpenAI(model_name="gpt-4", temperature=0.7, max_tokens=4096)

    answer_obj = answer_as_json(
        llm=llm,
        question=prompt_template.format(
            section_context=section["context"], relevant_docs=str(docs)
        ),
        schema=script_scene_schema,
    )

    return answer_obj["scenes"]


if __name__ == "__main__":
    # Read sample string from txt file

    print("generate_script")
