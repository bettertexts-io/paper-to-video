import logging

from langchain import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatOpenAI

import constants
from constants import OPENAI_API_KEY
from latex_to_chunks import chunk_latex_into_docs

llm = ChatOpenAI(model_name="gpt-4", temperature=0.2, max_tokens=4096)

DEFAULT_PROMPT_TEMPLATE = """Please summarize the following content concisely while retaining the core ideas:

{text}

SUMMARY:
"""

LATEX_SUMMARY_WITH_SECTIONS_PROMPT = """Summarize the following LaTeX academic paper. Exclude 'Conclusion', 'Bibliography', and 'References' sections. Include a list of other sections at the end of your answer:

{text}

SUMMARY WITH SECTIONS:
"""

CRAFT_SCRIPT_PROMPT = """Integrate the provided sections script into a single, cohesive narrator script. Ensure continuity and smooth transitions between sections. Exclude any scene descriptions and maintain a consistent tone suitable for a general audience:

{text}

PLAIN TEXT SCRIPT:
"""

"""
Summarize a text input by using the langchain refine summarization chain.
"""


def summarize_by_refine(text, prompt_template=None):
    docs = chunk_latex_into_docs(text)

    num_docs = len(docs)
    num_tokens_first_doc = llm.get_num_tokens(docs[0].page_content)

    print(
        f"Now we have {num_docs} documents and the first one has {num_tokens_first_doc} tokens"
    )

    if prompt_template is None:
        prompt_template = DEFAULT_PROMPT_TEMPLATE

    PROMPT = PromptTemplate(template=prompt_template, input_variables=["text"])

    refine_chain = load_summarize_chain(
        llm=llm, chain_type="refine", question_prompt=PROMPT, verbose=True
    )

    return refine_chain.run(docs)


"""
Summarize a text input by using the langchain map_reduce summarization chain.
"""


def summarize_by_map_reduce(text, prompt_template=None):
    docs = chunk_latex_into_docs(text)

    num_docs = len(docs)
    num_tokens_first_doc = llm.get_num_tokens(docs[0].page_content)

    print(
        f"Now we have {num_docs} documents and the first one has {num_tokens_first_doc} tokens"
    )

    if prompt_template is None:
        prompt_template = DEFAULT_PROMPT_TEMPLATE

    PROMPT = PromptTemplate(template=prompt_template, input_variables=["text"])

    # removed prompt cause it's no longer supported
    summary_chain = load_summarize_chain(llm=llm, chain_type="map_reduce")

    return summary_chain.run(docs)
