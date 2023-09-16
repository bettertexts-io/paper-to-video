from enum import Enum
import logging
import random
import uuid

from langchain import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.schema import Document
from langchain.vectorstores import Chroma

from .constants import *
from .latex_to_chunks import chunk_latex_into_sections
from .latex_to_text import extract_text_from_latex
from .paper_loader import paper_id_to_latex

llm = ChatOpenAI(
    model_name="gpt-4",
    # Prevent creativity
    temperature=0,
)


class EmbeddingsType(Enum):
    OPENSOURCE = "OPENSOURCE"
    OPENAI = "OPENAI"


EMBEDDDING_FUNCTION = EmbeddingsType.OPENAI

if EMBEDDDING_FUNCTION == EmbeddingsType.OPENSOURCE:
    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
elif EMBEDDDING_FUNCTION == EmbeddingsType.OPENAI:
    embedding_function = OpenAIEmbeddings()

DEFAULT_CONTEXT_PROMPT = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

{context}

Question: {question}

Craft a structured script with a narrator and scene descriptions. Avoid introductory phrases and conclusions. Ensure the content flows smoothly for a general audience:
"""

"""
Vectorize the paper in Chroma vector store using the given embedding function
"""


def random_uuid():
    return uuid.UUID(bytes=bytes(random.getrandbits(8) for _ in range(16)), version=4)


def vectorize_latex_in_chroma(paper_id: str, latex_input: str):
    # split it into chunks
    random.seed(paper_id)
    sections = chunk_latex_into_sections(latex_input)

    # Check if the paper has already been embedded in Chroma
    collection_name = "paper_" + paper_id
    # TODO: Fix this
    # if Chroma.get(persist_directory="chroma_db", collection_name=collection_name):
    #     logging.info(f"The collection for paper ID {paper_id} already exists. Skipping embedding.")
    #     return

    docs = []
    ids = []
    for section in sections:
        plain_text = extract_text_from_latex(section)
        cleaned_text = plain_text.strip().replace("\n", "")

        doc = Document(
            page_content=cleaned_text,
            metadata={"latex": section},
        )

        ids.append(str(random_uuid()))
        docs.append(doc)

    logging.info(docs)

    # load it into Chroma
    db = Chroma.from_documents(
        documents=docs,
        embedding=embedding_function,
        persist_directory="chroma_db",
        ids=ids,
        collection_name=collection_name,
    )
    db.persist()


def query_chroma(paper_id: str, input: str, number_of_results=4):
    # Load chroma
    collection_name = "paper_" + paper_id
    db = Chroma(
        persist_directory="chroma_db",
        embedding_function=embedding_function,
        collection_name=collection_name,
    )

    docs = db.similarity_search(input, k=number_of_results)

    return docs


def query_chroma_by_prompt(paper_id, question: str):
    # Load chroma
    docs = query_chroma(paper_id, question)

    # Query your database here
    chain = load_qa_chain(llm, chain_type="map_reduce")

    return chain.run(input_documents=docs, question=question)


def query_chroma_by_prompt_with_template(
    paper_id: str, question: str, prompt_template: str = DEFAULT_CONTEXT_PROMPT
):
    # Load chroma
    docs = query_chroma(paper_id, question, 2)

    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )
    chain = load_qa_chain(llm, chain_type="stuff", prompt=PROMPT)

    result = chain(
        {"input_documents": docs, "question": question}, return_only_outputs=True
    )
    return result["output_text"]


if __name__ == "__main__":
    # load a sample paper
    paper_id = "2205.14135"
    paper_content = paper_id_to_latex(paper_id)

    vectorize_latex_in_chroma(paper_id, paper_content)

    # Query paper by prompt
    question = "Summarize this paper"

    answer = query_chroma_by_prompt_with_template(paper_id, question)
    print(answer)
