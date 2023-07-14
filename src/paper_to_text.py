from pylatexenc.latex2text import LatexNodes2Text
from paper_loader import arxiv_id_to_latex

def extract_text_from_latex(latex_code):
    l2t = LatexNodes2Text()
    return l2t.latex_to_text(latex_code)


if __name__ == "__main__":
    paper = arxiv_id_to_latex("1706.03762")

    text = extract_text_from_latex(paper)
    print(text)
