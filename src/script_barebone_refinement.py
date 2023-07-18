from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.vectorstores import Chroma

def generate_script(summary):
    """
    Given the summary of the paper, generate a basic video script.
    This function involves splitting the sections into chunks and querying the 
    chroma vector database for each section. The result is a script for a video
    """
    # Remove leading/trailing whitespace and split by newline
    sections = summary.strip().split('\n')

    # Now, we'll strip off the leading numbering from each section title
    section_names = [s.split('. ', 1)[1] for s in sections]

    script = {}

    for section_name in section_names:
        # Query your database here
        print(section_name)
        
    return script


if __name__ == "__main__":
    # Read sample string from txt file

    input = """
        1. Introduction
        2. Background
        3. Model Architecture
        4. Why Self-Attention
        5. Training
        6. Results
        7. Conclusion
        8. Self-Attention
        9. Comparison with Other Models
        10. Attention Visualizations
        11. Comparison of Self-Attention Layers to Recurrent and Convolutional Layers
        12. Computational Performance and Path Lengths
        13. Two Feed-Forward Layers = Attention over Parameters
        14. Machine Translation
        15. Model Variations
        16. English Constituency Parsing
        17. Justification of the Scaling Factor in Dot-product Attention
        18. Training Data and Batching
        19. Hardware and Schedule
        20. Optimizer
        21. Regularization
        22. Model Architecture
        23. Encoder and Decoder Stacks
        24. Attention
        25. Scaled Dot-Product Attention
        26. Dot-Product Attention
        27. Multi-Head Attention
        28. Applications of Attention in the Model
        29. Position-wise Feed-Forward Networks
        30. Multiple Attention Heads
        31. Embeddings and Softmax
        32. Positional Encoding.
        """

    print(generate_script(input))
        