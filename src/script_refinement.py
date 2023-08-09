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
        You are tasked to create a video scenes from a section description and some context documents. Scenes represent a change of the displayed content in a video.
        
        Prioritize the following guidelines:
        - Generate seperate scenes based on the given context description.
        - Use the summary's content to derive at least 5 distinct video sections.
        - Each section has different attributes, which will be used to generate the voice, image, caption components of the video.
        - Optimize the scenes for viewer engagement without compromising accuracy.
        - Be precise when it comes to the speakerScript it will be used to generate the voice component of the video.
        - The stockFootageQuery will be used to query a stock footage database. Every scene can only have one stock image resource.
        - There is currently only one possible scene type: TEXT
        - Let the Narrator speak as the author of the paper. Avoid phrases like "the paper says" or "the author says".

        ---Section context---
        {section_context}
                                    
        ---Relevant document snippets---
        {relevant_docs}
    """
    )

    prompt_template = PromptTemplate.from_template(template=text_template)

    llm = ChatOpenAI(model_name="gpt-4", temperature=0.6, max_tokens=4096)

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
