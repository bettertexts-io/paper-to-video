from langchain.text_splitter import LatexTextSplitter

from .paper_loader import paper_id_to_latex


def chunk_latex_into_sections(latex_input: str):
    # split it into chunks
    text_splitter = LatexTextSplitter(chunk_size=8000, chunk_overlap=800)
    chunks = text_splitter.split_text(latex_input)

    return chunks


def chunk_latex_into_docs(latex_input: str):
    text_splitter = LatexTextSplitter(chunk_size=8000, chunk_overlap=800)
    docs = text_splitter.create_documents([latex_input])

    return docs


if __name__ == "__main__":
    # load the document
    paper_content = paper_id_to_latex("1706.03762")

    chunks = chunk_latex_into_sections(paper_content)
    print(chunks)
