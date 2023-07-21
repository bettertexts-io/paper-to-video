from langchain import PromptTemplate
from answer_as_json import answer_as_json
from constants import OPENAI_API_KEY
from langchain.chat_models import ChatOpenAI

from script import script_schema


llm = ChatOpenAI(
    model_name="gpt-4",
    # TODO: Find best temperature setting here
    temperature=0.7,
    max_tokens=4096
)

def generate_barebone_script(summary: str) -> dict:
    text_template = """Write a barebone script for a short video based on a summary and the list of sections in a document. 
    Note of all the sections of the paper is at the end of the paper. 
    This step is only about creating the barebone video structure. 
    You don't have to stick to the order of the sections in the paper. If needed, mix things up a bit, to make the video more engaging. 
    Supply context for the sections, so that other editor understand, what the section is about. Don't include details like captions or image references here.
    The video should be optimized for engagement, but not without sacrificing accuracy.
    Use best practices for creating an engaging video when creating the video structure. Come up with at least 5 sections.
    
    The summary:
    {summary}
    """
    prompt_template = PromptTemplate.from_template(template=text_template)

    answer_obj = answer_as_json(llm=llm, question=prompt_template.format(summary=summary), schema=script_schema(exclude_scenes=True))

    return answer_obj
