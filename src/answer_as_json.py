from langchain.chains import create_extraction_chain, create_extraction_chain_pydantic
from langchain.chat_models import ChatOpenAI


def answer_as_json(llm: ChatOpenAI, question: str, schema: any):
    chain = create_extraction_chain(schema=schema, llm=llm)
    return chain.run(question)[0]
