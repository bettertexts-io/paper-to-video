import logging
from langchain_summarize import LATEX_SUMMARY_WITH_SECTIONS_PROMPT, summarize_by_map_reduce
from paper_loader import arxiv_id_to_latex

logging.basicConfig(level=logging.INFO)

latex = arxiv_id_to_latex("1706.03762")

# Summarize the paper using langchain map_reduce summarization
# The summary includes a list of the sections of the paper at the end
summary = summarize_by_map_reduce(latex, LATEX_SUMMARY_WITH_SECTIONS_PROMPT)

# Turn the summary into a barebone video script structure with approximated lengths of the sections




# Generate a detailed summary for each section of the generated script structure




# Generate a detailed script snipped with resources for each section of the generated script structure
# Feed in the generated focussed summaries for each section





# Render the script into a video