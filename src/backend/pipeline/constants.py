import os

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
POE_TOKEN = os.getenv("POE_TOKEN")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
SERP_API_KEY = os.getenv("SERP_API_KEY")

MOCK_SUMMARY = """The paper "Attention Is All You Need" introduces a new network architecture called the Transformer, which relies solely on attention mechanisms and does not use recurrence and convolutions. The authors demonstrate that this model outperforms existing models in terms of quality, parallelizability, and training time. The Transformer model achieved high BLEU scores on the WMT 2014 English-to-German and English-to-French translation tasks and was also successfully applied to English constituency parsing tasks. The authors discuss the advantages of self-attention over other models and provide visualizations of the attention mechanism in the Transformer model. They also discuss the computational performance and path lengths of different layer types in machine learning models, specifically focusing on self-attention, recurrent, and convolutional layers. The authors propose that two feed-forward layers can be seen as a form of attention and experiment with replacing the position-wise feed-forward networks with attention layers. The paper also discusses the training regime for models, focusing on the standard WMT 2014 English-German dataset and the WMT 2014 English-French dataset. The training was done on a machine with 8 NVIDIA P100 GPUs, using the Adam optimizer. The paper also discusses the use of three types of regularization during training: Residual Dropout, Attention Dropout, and Label Smoothing.
        Sections of the document include:
        1. Introduction
        2. Background
        3. Model Architecture
        4. Why Self-Attention
        5. Training
        6. Results
"""

print(f"OPENAI_API_KEY: {OPENAI_API_KEY}")


VIDEO_FPS = 24
