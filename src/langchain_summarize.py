import logging
import constants

from langchain import PromptTemplate
from constants import OPENAI_API_KEY
from langchain.chat_models import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain

from latex_to_chunks import chunk_latex_into_docs


llm = ChatOpenAI(
    model_name="gpt-4",
    temperature=0,
    max_tokens=4096
)

DEFAULT_PROMPT_TEMPLATE = """Write a concise summary of the following:


{text}


CONCISE SUMMARY IN ENGLISH:"""


LATEX_SUMMARY_WITH_SECTIONS_PROMPT = """Write a concise summary of the following paper written in latex. Do not include sections like 'Conclusion', 'Bibliography' and 'References'. Always include the other sections of the document as a list in your answer:


{text}


CONCISE SUMMARY WITH SECTIONS AS LIST AT THE END:"""


"""
Summarize a text input by using the langchain refine summarization chain.
"""
def summarize_by_refine(text, prompt_template=None):    
    docs = chunk_latex_into_docs(text)

    num_docs = len(docs)
    num_tokens_first_doc = llm.get_num_tokens(docs[0].page_content)

    logging.info(f"Now we have {num_docs} documents and the first one has {num_tokens_first_doc} tokens")

    if prompt_template is None:
        prompt_template = DEFAULT_PROMPT_TEMPLATE

    PROMPT = PromptTemplate(template=prompt_template, input_variables=["text"])

    refine_chain = load_summarize_chain(llm=llm, chain_type='refine', question_prompt=PROMPT, verbose=True)

    return refine_chain.run(docs)


"""
Summarize a text input by using the langchain map_reduce summarization chain.
"""
def summarize_by_map_reduce(text, prompt_template=None):
    docs = chunk_latex_into_docs(text)

    num_docs = len(docs)
    num_tokens_first_doc = llm.get_num_tokens(docs[0].page_content)

    logging.info(f"Now we have {num_docs} documents and the first one has {num_tokens_first_doc} tokens")

    if prompt_template is None:
        prompt_template = DEFAULT_PROMPT_TEMPLATE

    PROMPT = PromptTemplate(template=prompt_template, input_variables=["text"])

    summary_chain = load_summarize_chain(llm=llm, chain_type='map_reduce', prompt=PROMPT)

    return summary_chain.run(docs)
