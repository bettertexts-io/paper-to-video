import json

from langchain import PromptTemplate
from constants import OPENAI_API_KEY
from langchain.chat_models import ChatOpenAI
from langchain.chains import create_extraction_chain, create_extraction_chain_pydantic

from script import script_schema
from tmp import tmp_barebone_script_path


llm = ChatOpenAI(
    model_name="gpt-4",
    temperature=0.8,
    max_tokens=4096
)

def answer_as_json(question: str, schema: any):
    chain = create_extraction_chain(schema=schema, llm=llm)
    return chain.run(question)[0]

def generate_barbone_script(summary: str) -> dict:
    text_template = """Write a barebone script for a short video based on a summary and the list of sections in a document. 
    Note of all the sections of the paper is at the end of the paper. 
    This step is only about creating the barebone video structure. 
    You don't have to stick to the order of the sections in the paper. If needed, mix things up a bit, to make the video more engaging. 
    Supply context for the sections, so that other editor understand, what the section is about. Don't include details like captions or image references here.
    The video should be optimized for engagement, but not without sacrificing accuracy.
    Use best practices for creating an engaging video when creating the video structure.
    
    The summary:
    {summary}
    """
    prompt_template = PromptTemplate.from_template(template=text_template)

    answer_obj = answer_as_json(prompt_template.format(summary=summary), script_schema(exclude_scenes=True))

    return answer_obj