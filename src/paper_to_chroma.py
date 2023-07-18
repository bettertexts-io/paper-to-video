import os
from enum import Enum
from langchain import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma

from constants import OPENAI_API_KEY
from paper_loader import arxiv_id_to_latex
from paper_to_text import extract_text_from_latex

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

llm = ChatOpenAI(
    model_name="gpt-4",
    temperature=0.5,
    max_tokens=4096
)

class EmbeddingsType(Enum):
    OPENSOURCE = "OPENSOURCE"
    OPENAI = "OPENAI"

"""
Vectorize the paper in Chroma vector store using the given embedding function
"""
def vectorize_paper_in_chroma(input: str, embedding_function: EmbeddingsType = EmbeddingsType.OPENSOURCE):
    # split it into chunks
    text_splitter = RecursiveCharacterTextSplitter(separators=["\section", "\subsection", "\n"], chunk_size=10000, chunk_overlap=500)
    texts = text_splitter.split_text(input)

    # create the embedding function
    if embedding_function == EmbeddingsType.OPENSOURCE:
        embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    elif embedding_function == EmbeddingsType.OPENAI:
        embedding_function = OpenAIEmbeddings()

    # TODO: render lex into plain text before generating the embeddings
    
    # load it into Chroma
    db = Chroma.from_texts(texts, embedding_function, persist_directory="../chroma_db")
    db.persist()


def query_paper_by_section_name(section_name: str, embedding_function: EmbeddingsType = EmbeddingsType.OPENSOURCE):
    # create the embedding function
    if embedding_function == EmbeddingsType.OPENSOURCE:
        embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    elif embedding_function == EmbeddingsType.OPENAI:
        embedding_function = OpenAIEmbeddings()

    # Load chroma
    db = Chroma(persist_directory="../chroma_db", embedding_function=embedding_function)

    prompt_template = """
    Given the key points and most important details of the '{context}' section from a scientific paper, 
    generate an informative and engaging script for a video presentation. Ensure the script is concise,
    understandable for a general audience, and highlights the main takeaways.

    Key Points and Details: 

    {question}
    """

    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    # Query your database here
    chain_type_kwargs = {"prompt": PROMPT}
    qa = RetrievalQA.from_chain_type(llm, chain_type="stuff", retriever=db.as_retriever(), chain_type_kwargs=chain_type_kwargs)

    query = "What is in the paper about: " + section_name + "?"
    qa.run(query)


if __name__ == "__main__":
    # load the document and split it into chunks
    paper = arxiv_id_to_latex("1706.03762")

    text = extract_text_from_latex(paper)

    vectorize_paper_in_chroma(text)

