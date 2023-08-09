from langchain.text_splitter import RecursiveCharacterTextSplitter

from paper_loader import arxiv_id_to_latex

def chunk_latex_into_sections(latex_input: str):
    # split it into chunks
    text_splitter = RecursiveCharacterTextSplitter(separators=["\section", "\subsection"], chunk_size=10000, chunk_overlap=500)
    chunks = text_splitter.split_text(latex_input)

    return chunks


def chunk_latex_into_docs(latex_input: str):
    text_splitter = RecursiveCharacterTextSplitter(separators=["\section", "\subsection"], chunk_size=10000, chunk_overlap=500)
    docs = text_splitter.create_documents([latex_input])

    return docs


if __name__ == "__main__":
    # load the document
    paper_content = arxiv_id_to_latex("1706.03762")

    chunks = chunk_latex_into_sections(paper_content)
    print(chunks)