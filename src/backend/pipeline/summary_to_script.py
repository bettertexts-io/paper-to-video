import textwrap

from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI

from .answer_as_json import answer_as_json
from .constants import OPENAI_API_KEY
from .script import generate_script_schema

llm = ChatOpenAI(model_name="gpt-4", temperature=0.8)


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
      Convert the summary into a Yannic Kilcher-style script, which delves into the topic's depth. Follow these steps to craft a script:

      1. **Introduction**:
      a) Begin with a bold statement or question highlighting the topic's importance.
      b) Briefly state the scientific paper's main focus.

      2. **Segmentation**:
      a) Split the summary into 4-5 distinct sections.
      b) For each section, create:
         - **Title**: A descriptive header.
         - **Context**: Detailed, clear content that offers a comprehensive view of the discussed aspects.

      3. **Flow**:
      a) Ensure smooth transitions between sections.
      b) Maintain a strong narrative without referencing visuals.

      4. **Conclusion**:
      a) Summarize the discussed key points.
      b) End with a thought-provoking question or statement.

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
