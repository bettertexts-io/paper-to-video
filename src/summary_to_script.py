import textwrap
from typing import Dict

from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI

from answer_as_json import answer_as_json
from constants import OPENAI_API_KEY
from script import script_schema

llm = ChatOpenAI(model_name="gpt-4", temperature=0.7, max_tokens=4096)


def generate_barebone_script(summary: str):
    """
    Generate a barebone video script based on the provided summary of a scientific paper.

    Parameters:
    - summary (str): Summary of a scientific paper.

    Returns:
    - dict: A dictionary containing structured video script sections.
    """

    text_template = textwrap.dedent(
    """
    ---INSTRUCTIONS---
    In a world inundated with information, it's essential to present content in a digestible and engaging way. With this in mind, your task is to create a structured and captivating barebone video script. Follow the guidelines below to transform a summary into an exciting narrative:

    1. **Introduction**: Start with a compelling introduction that hooks the viewer. Briefly outline the subject of the video and why it matters.

    2. **Convert the Summary into Video Sections**: Break down the summary into at least five distinct video sections. These sections should contain:
        a) **Title**: A relevant and intriguing title for each section.
        b) **Context**: Explain the content of the section in a way that maintains viewer interest without sacrificing accuracy.

    3. **Optimization for Engagement**: Arrange the sections coherently and craft the content to keep the viewer engaged. Be creative but remain true to the facts.

    4. **Avoid Visual References**: Focus on the script's verbal content. Do not include captions or image references at this stage.

    5. **Conclusion**: Summarize everything discussed in the video. Wrap up with a closing statement that leaves an impression.

    By adhering to these guidelines, you'll craft a script that informs and entertains.

    ---SUMMARY---
    {input}
    """)

    prompt_template = PromptTemplate.from_template(template=text_template)
    schema = script_schema(exclude_scenes=True)

    answer_obj = answer_as_json(
        llm=llm,
        schema=schema,
        prompt=prompt_template,
        input=summary
    )

    return answer_obj
