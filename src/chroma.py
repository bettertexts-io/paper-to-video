import os
from enum import Enum
from langchain import PromptTemplate
from langchain.schema import Document
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.chains.question_answering import load_qa_chain
from langchain.vectorstores import Chroma

from constants import *
from latex_to_chunks import chunk_latex_into_sections
from latex_to_text import extract_text_from_latex

llm = ChatOpenAI(
    model_name="gpt-4",
    # Prevent creativity
    temperature=0,
    max_tokens=4096
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
def vectorize_latex_in_chroma(latex_input: str):
    # split it into chunks
    sections = chunk_latex_into_sections(latex_input)

    docs = []
    for section in sections:
        plain_text = extract_text_from_latex(section)
        cleaned_text = plain_text.strip().replace('\n', '')

        doc = Document(
            page_content=cleaned_text,
            metadata={"latex": section},
        )

        docs.append(doc)
    
    # load it into Chroma
    db = Chroma.from_documents(docs, embedding_function, persist_directory="../chroma_db")
    db.persist()


def query_chroma(input: str, number_of_results = 5):
    # Load chroma
    db = Chroma(persist_directory="../chroma_db", embedding_function=embedding_function)

    docs = db.similarity_search(input, k=number_of_results)

    return docs


def query_chroma_by_prompt(question: str):
    # Load chroma
    docs = query_chroma(question)

    # Query your database here
    chain = load_qa_chain(llm, chain_type="map_reduce", verbose=True)

    return chain.run(input_documents=docs, question=question)


def query_chroma_by_prompt_with_template(question: str, prompt_template: str = DEFAULT_CONTEXT_PROMPT):
    # Load chroma
    docs = query_chroma(question, 2)

    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )
    chain = load_qa_chain(llm, chain_type="stuff", prompt=PROMPT, verbose=True)

    result = chain({"input_documents": docs, "question": question}, return_only_outputs=True)
    return result["output_text"]


if __name__ == "__main__":
    # # load a sample paper
    # paper_content = arxiv_id_to_latex("1706.03762")

    # vectorize_latex_in_chroma(paper_content)

    # # Query paper by prompt
    keyword = "Introduction"

    answer = query_chroma_by_prompt_with_template(keyword)
    logging.info(answer)




