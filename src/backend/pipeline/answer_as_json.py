from langchain import BasePromptTemplate
from langchain.chains.openai_functions import create_structured_output_chain
from langchain.chat_models import ChatOpenAI


def answer_as_json(llm: ChatOpenAI, schema: any, prompt: BasePromptTemplate, input: any):
    chain = create_structured_output_chain(output_schema=schema, llm=llm, prompt=prompt, verbose=True)
    return chain.run(input)
