from transformers import pipeline
from paper_loader import arxiv_id_to_latex

def summarize_text(text):
    summarizer = pipeline('summarization')

    return summarizer(text, max_length=2000, min_length=1500, do_sample=False)[0]['summary_text']


if __name__ == "__main__":
      # Text to be summarized
      text = arxiv_id_to_latex("1706.03762")

      print(summarize_text(text))
