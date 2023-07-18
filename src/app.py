import json
import logging
from langchain_summarize import LATEX_SUMMARY_WITH_SECTIONS_PROMPT, summarize_by_map_reduce
from paper_loader import arxiv_id_to_latex
from summary_to_script import generate_barbone_script
from tmp import tmp_barebone_script_path

logging.basicConfig(level=logging.INFO)

paper_id = "1706.03762"

latex = arxiv_id_to_latex(paper_id)

# Summarize the paper using langchain map_reduce summarization
# The summary includes a list of the sections of the paper at the end
# summary = summarize_by_map_reduce(latex, LATEX_SUMMARY_WITH_SECTIONS_PROMPT)
# print(summary)

summary = """The paper "Attention Is All You Need" introduces a new network architecture called the Transformer, which relies solely on attention mechanisms and does not use recurrence and convolutions. The authors demonstrate that this model outperforms existing models in terms of quality, parallelizability, and training time. The Transformer model achieved high BLEU scores on the WMT 2014 English-to-German and English-to-French translation tasks and was also successfully applied to English constituency parsing tasks. The authors discuss the advantages of self-attention over other models and provide visualizations of the attention mechanism in the Transformer model. They also discuss the computational performance and path lengths of different layer types in machine learning models, specifically focusing on self-attention, recurrent, and convolutional layers. The authors propose that two feed-forward layers can be seen as a form of attention and experiment with replacing the position-wise feed-forward networks with attention layers. The paper also discusses the training regime for models, focusing on the standard WMT 2014 English-German dataset and the WMT 2014 English-French dataset. The training was done on a machine with 8 NVIDIA P100 GPUs, using the Adam optimizer. The paper also discusses the use of three types of regularization during training: Residual Dropout, Attention Dropout, and Label Smoothing.

Sections of the document include:
1. Introduction
2. Background
3. Model Architecture
4. Why Self-Attention
5. Training
6. Results
7. Conclusion
8. Acknowledgements
9. Bibliography
10. References
11. Visualizations
12. Parameter Attention
13. Sqrt_d_trick
14. Attention Visualizations
15. Computational Performance and Path Lengths
16. Two Feed-Forward Layers = Attention over Parameters
17. Machine Translation
18. Model Variations
19. English Constituency Parsing
20. Application of Transformer Model to English Constituency Parsing
21. Justification of the Scaling Factor in Dot-product Attention
22. Training Data and Batching
23. Hardware and Schedule
24. Optimizer
25. Regularization
26. Encoder and Decoder Stacks
27. Attention
28. Comparison of Additive Attention and Dot-Product Attention
29. Multi-Head Attention
30. Applications of Attention in the Model
31. Position-wise Feed-Forward Networks
32. Multiple Attention Heads
33. Embeddings and Softmax
34. Positional Encoding.
"""

# Turn the summary into a barebone video script structure with approximated lengths of the sections
script = generate_barbone_script(summary=summary)

barebone_path = tmp_barebone_script_path(paper_id)
with open(barebone_path, 'w') as f:
    json.dump(script, f, indent=4)

print(script)

# Generate a detailed summary for each section of the generated script structure




# Generate a detailed script snipped with resources for each section of the generated script structure
# Feed in the generated focussed summaries for each section





# Render the script into a video