from langchain import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatOpenAI

import logging
from time import time
from typing import Optional, List

from .constants import OPENAI_API_KEY
from .latex_to_chunks import chunk_latex_into_docs

llm = ChatOpenAI(model_name="gpt-4", temperature=0)

DEFAULT_PROMPT_TEMPLATE = """Please summarize the following content concisely while retaining the core ideas:

{text}

SUMMARY:
"""

MAP_SUMMARY_PROMPT = """
 Write a concise summary of the following:
 "{text}"
 CONCISE SUMMARY:
 """

COMBINE_SUMMARY_PROMPT = """Please provide a summary of the following academic paper which is written in LaTeX, adhering to the structure outlined below. Make sure to omit the 'Conclusion', 'Bibliography', and 'References' sections. Focus on summarizing the 'Introduction', 3-4 main sections, and then provide an end summary. Include a list of the other sections at the end of your response:

{text}

SUMMARY STRUCTURE:
1. Introduction: Provide an overview of the topic, objectives, and background.
2. Main Section 1: Detail the first key area or research question.
3. Main Section 2: Summarize the second major theme or methodology.
4. Main Section 3: Explain the third critical point or findings.
5. (Optional) Main Section 4: If present, describe the fourth significant aspect.
6. End Summary: Conclude with the key insights, applications, or implications.
7. Other Sections: List any additional sections found in the paper that were not summarized.

SUMMARY WITH SECTIONS:
"""

CRAFT_SCRIPT_PROMPT = """Integrate the provided sections script into a single, cohesive narrator script. Ensure continuity and smooth transitions between sections. Exclude any scene descriptions and maintain a consistent tone suitable for a general audience:

{text}

PLAIN TEXT SCRIPT:
"""

"""
Summarize a text input by using the langchain refine summarization chain.
"""


def summarize_by_refine(text: str, prompt_template: Optional[str] = None):
    """
    This function takes a LaTeX text and a prompt template, chunks the text into documents,
    and runs a summarization refine chain on these documents.

    Parameters:
    text (str): The input LaTeX text to be processed.
    prompt_template (str, optional): The prompt template to be used in the summarization. Defaults to None.

    Returns:
    List[str]: The summarized documents.
    """
    start_time = time()

    docs = chunk_latex_into_docs(text)

    num_docs = len(docs)
    num_tokens_first_doc = llm.get_num_tokens(docs[0].page_content)

    logging.info(
        f"Now we have {num_docs} documents and the first one has {num_tokens_first_doc} tokens"
    )

    if prompt_template is None:
        prompt_template = DEFAULT_PROMPT_TEMPLATE

    PROMPT = PromptTemplate(template=prompt_template, input_variables=["text"])

    refine_chain_start_time = time()
    refine_chain = load_summarize_chain(
        llm=llm, chain_type="refine", question_prompt=PROMPT
    )
    logging.info(
        f"Time taken to load refine chain: {time() - refine_chain_start_time} seconds"
    )

    run_chain_start_time = time()
    result = refine_chain.run(docs)
    logging.info(
        f"Time taken to run refine chain: {time() - run_chain_start_time} seconds"
    )

    logging.info(f"Total time taken: {time() - start_time} seconds")

    return result


"""
Summarize a text input by using the langchain map_reduce summarization chain.
"""


def summarize_by_map_reduce(
    text, map_prompt_template=None, combine_prompt_template=None
):
    docs = chunk_latex_into_docs(text)

    num_docs = len(docs)
    num_tokens_first_doc = llm.get_num_tokens(docs[0].page_content)

    print(
        f"Now we have {num_docs} documents and the first one has {num_tokens_first_doc} tokens"
    )

    map_promopt = PromptTemplate(template=map_prompt_template, input_variables=["text"])
    combine_prompt = PromptTemplate(
        template=combine_prompt_template, input_variables=["text"]
    )

    # removed prompt cause it's no longer supported
    summary_chain = load_summarize_chain(
        llm=llm,
        chain_type="map_reduce",
        map_prompt=map_promopt,
        combine_prompt=combine_prompt,
    )

    return summary_chain.run(docs)
