import os
from enum import Enum
from langchain import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.schema import Document
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.chains.question_answering import load_qa_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma

from constants import OPENAI_API_KEY
from paper_loader import arxiv_id_to_latex
from latex_to_text import extract_text_from_latex

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

llm = ChatOpenAI(
    model_name="gpt-4",
    temperature=0.5,
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
def vectorize_paper_in_chroma(latex_input: str):
    # split it into chunks
    text_splitter = RecursiveCharacterTextSplitter(separators=["\section", "\subsection", "\n"], chunk_size=10000, chunk_overlap=500)
    latex_chunks = text_splitter.split_text(latex_input)

    docs = []
    for chunk in latex_chunks:
        plain_text = extract_text_from_latex(chunk)
        cleaned_text = plain_text.strip().replace('\n', '')

        doc = Document(
            page_content=cleaned_text,
            metadata={"latex": chunk},
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


def query_paper_by_prompt(question: str, context_prompt = DEFAULT_CONTEXT_PROMPT):
    # Load chroma
    docs = query_chroma(question, 2)

    # prompt_template = context_prompt

    # PROMPT = PromptTemplate(
    #     template=prompt_template, input_variables=["context", "question"]
    # )

    # Query your database here
    chain = load_qa_chain(llm, chain_type="map_reduce", verbose=True)

    return chain.run(input_documents=docs, question=question)


if __name__ == "__main__":
    # load the document and split it into chunks 
    # paper = arxiv_id_to_latex("1706.03762")

    # vectorize_paper_in_chroma(paper)

    # Query chroma
    # docs = query_chroma("position-wise feed-forward networks", 1)
    # print(len(docs))

    # Query paper by prompt
    answer = query_paper_by_prompt("What is this paper about?")
    print(answer)




