import logging

from langchain import PromptTemplate
from constants import OPENAI_API_KEY
from langchain.chat_models import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter


llm = ChatOpenAI(
    model_name="gpt-4",
    temperature=0,
    max_tokens=4096
)

DEFAULT_PROMPT_TEMPLATE = """Write a concise summary of the following:


{text}


CONCISE SUMMARY IN ENGLISH:"""

def summarize_by_map_reduce(text, prompt_template=None):    
    text_splitter = RecursiveCharacterTextSplitter(separators=["\section", "\subsection", "\n"], chunk_size=10000, chunk_overlap=500)
    docs = text_splitter.create_documents([text])

    num_docs = len(docs)
    num_docs = len(docs)

    num_tokens_first_doc = llm.get_num_tokens(docs[0].page_content)

    logging.info(f"Now we have {num_docs} documents and the first one has {num_tokens_first_doc} tokens")

    if prompt_template is None:
        prompt_template = DEFAULT_PROMPT_TEMPLATE

    PROMPT = PromptTemplate(template=prompt_template, input_variables=["text"])

    summary_chain = load_summarize_chain(llm=llm, chain_type='map_reduce', map_prompt=PROMPT, combine_prompt=PROMPT)

    return summary_chain.run(docs)

with open("testlatex.txt", "r") as f:
    text = f.read()

prompt_template = """Write a concise summary of the following paper written in latex. Always include the sections of the document as a list in your answer:


{text}


CONCISE SUMMARY WITH SECTIONS AS LIST AT THE END:"""

print(summarize_by_map_reduce(text, prompt_template))