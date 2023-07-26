import os
from enum import Enum
from langchain import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.schema import Document
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.chains.question_answering import load_qa_chain
from langchain.vectorstores import Chroma

from constants import OPENAI_API_KEY
from latex_to_chunks import chunk_latex_into_sections
from paper_loader import arxiv_id_to_latex
from latex_to_text import extract_text_from_latex

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

llm = ChatOpenAI(
    model_name="gpt-4",
    temperature=0.6,
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

DEFAULT_CONTEXT_PROMPT = """
Given the key points and most important details section from a scientific paper, 
generate an informative and engaging script for a video presentation. Ensure the script is concise,
understandable for a general audience, and highlights the main takeaways:

Context:

{context}

Key Points and Details: 

{question}
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
    docs = query_chroma(question, 2)

    # Query your database here
    chain = load_qa_chain(llm, chain_type="map_reduce", verbose=True)

    return chain.run(input_documents=docs, question=question)


if __name__ == "__main__":
    # load a sample paper
    paper_content = arxiv_id_to_latex("1706.03762")

    vectorize_latex_in_chroma(paper_content)

    # Query chroma
    docs = query_chroma("position-wise feed-forward networks", 1)
    print(len(docs))

    # # Query paper by prompt
    # answer = query_paper_by_prompt("What is this paper about?")
    # print(answer)




