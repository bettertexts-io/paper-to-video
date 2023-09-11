import textwrap

from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI

from .answer_as_json import answer_as_json
from .constants import OPENAI_API_KEY
from .script import generate_script_schema

llm = ChatOpenAI(model_name="gpt-4", temperature=0.7)


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
    Channeling Yannic Kilcher's analytical style, transform the given summary into a detailed video script:

    1. **Introduction**: Start with a question or statement about the topic's importance.
    2. **Segmentation**: Divide the summary into at least five sections. Each should have:
        a) **Title**: A meaningful header.
        b) **Context**: Detailed content, balancing depth with clarity.
    3. **Flow**: Ensure logical progression between sections.
    4. **Avoid Visuals**: Focus on narrative content; omit visual references.
    5. **Conclusion**: Summarize and end with a thought-provoking question or statement.

    ---SUMMARY---
    {input}
    """
    )

    prompt_template = PromptTemplate.from_template(template=text_template)
    schema = generate_script_schema(exclude_scenes=True)

    answer_obj = answer_as_json(
        llm=llm, schema=schema, prompt=prompt_template, input=summary
    )

    return answer_obj
