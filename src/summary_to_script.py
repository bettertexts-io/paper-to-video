import textwrap
from typing import Dict

from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI

from answer_as_json import answer_as_json
from constants import OPENAI_API_KEY
from script import script_schema

llm = ChatOpenAI(model_name="gpt-4", temperature=0.7, max_tokens=4096)


def generate_barebone_script(summary: str) -> Dict[str, any]:
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
        Create a structured and engaging barebone video script. Prioritize the following guidelines:
        - Convert the below summary into video sections.
        - Use the summary's content to derive at least 5 distinct video sections.
        - Each section should have its own title and context.
        - Optimize the sections for viewer engagement without compromising accuracy.
        - The section order can be re-arranged for better coherence.
        - Avoid adding captions or image references at this stage.

        ---SUMMARY---
        {summary}
    """
    )

    prompt_template = PromptTemplate.from_template(template=text_template)

    answer_obj = answer_as_json(
        llm=llm,
        question=prompt_template.format(summary=summary),
        schema=script_schema(exclude_scenes=True),
    )

    return answer_obj
