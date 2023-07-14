from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma

from paper_loader import arxiv_id_to_latex
from paper_to_text import extract_text_from_latex

def vectorize_paper_in_chroma(input: str):
    # split it into chunks
    text_splitter = RecursiveCharacterTextSplitter(separators=["\section", "\subsection", "\n"], chunk_size=10000, chunk_overlap=500)
    texts = text_splitter.split_text(input)

    # create the open-source embedding function
    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    # load it into Chroma
    db = Chroma.from_texts(texts, embedding_function, persist_directory="../chroma_db")
    db.persist()


if __name__ == "__main__":
    # load the document and split it into chunks
    paper = arxiv_id_to_latex("1706.03762")

    text = extract_text_from_latex(paper)

    vectorize_paper_in_chroma(text)

