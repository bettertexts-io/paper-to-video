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


def generate_script_scenes(section: ScriptSection, last_two_sections: tuple[str, str]):
    """
    Given the script of a section, generate a list of scenes for the video.
    """

    docs = query_chroma_by_prompt(section["title"])
    print(docs)

    text_template = textwrap.dedent(
    """
    ---INSTRUCTIONS---
    Using the provided section context and related document snippets, you are to design engaging video scenes. Adhere to the following:

    - Craft at least 4 distinct scenes based on the section context.
    - Each scene should encompass:
        * A concise speakerScript, which will be vocalized in the video.
        * A stockFootageQuery that's specific enough to identify a relevant stock image on platforms like Pixabay. For abstract concepts, choose descriptors that are clear, unambiguous, and closely related to the topic.
        * Note: The scene type is TEXT.
    - Avoid using the same stockFootageQuery for multiple scenes.
    - Narrate in the style of the paper's author. Refrain from phrases like "the paper mentions" or "according to the author."
    - Prioritize viewer engagement while ensuring the content's factual integrity.
    - Make content engaging and understandable for a non-scientific audience, ensuring factual accuracy. Avoid repetitiveness.
    
    ---PREVIOUS SECTIONS (For Reference)---
    {last_two_sections}

    ---SECTION CONTEXT---
    {section_context}

    ---DOCUMENT SNIPPETS---
    {relevant_docs}
    """
    )

    prompt_template = PromptTemplate.from_template(template=text_template)

    llm = ChatOpenAI(model_name="gpt-4", temperature=0.7, max_tokens=4096)

    answer_obj = answer_as_json(
        llm=llm,
        schema=script_scene_schema,
        prompt=prompt_template,
        input=({'section_context': section["context"], 'relevant_docs': str(docs), 'last_two_sections': last_two_sections}),
    )

    return answer_obj["scenes"]


if __name__ == "__main__":
    # Read sample string from txt file

    print("generate_script")
