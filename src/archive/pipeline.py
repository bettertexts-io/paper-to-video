from concurrent.futures import ThreadPoolExecutor
from archive.extract_paper import pdf_to_text
from archive.text_to_script import text_to_script
from text_to_animation import create_scene
from text_to_voice import text_to_voice
from vid_render import render_vid

script = {
    "A computer screen filled with lines of code, then transitions to the title 'Attention Is All You Need'": "text",
    "Hello everyone! Today, we are going to talk about a ground-breaking paper by researchers from Google Brain and Google Research titled 'Attention Is All You Need'.": "text",
    "The paper proposes a new simple network architecture called the Transformer which is based solely on attention mechanisms. The Transformer model dispenses with recurrence and convolutions entirely.": "text",
    "The researchers found that using attention mechanisms allows the model to draw global dependencies between input and output. It also allows for more parallelization, reducing training times significantly.": "text",
    "The paper highlights the issues with recurrent models, which typically factor computation along the symbol positions of the input and output sequences. This inherently sequential nature prevents parallelization within training examples, which becomes critical at longer sequence lengths.": "text",
    "On the other hand, attention mechanisms allow modeling of dependencies without regard to their distance in the input or output sequences.": "text",
    "The researchers tested the Transformer on two machine translation tasks. The results showed these models to be superior in quality while requiring significantly less time to train.": "text",
    "The Transformer model achieved a 28.4 BLEU score on the WMT 2014 English-to-German translation task, improving over the existing best results by over 2 BLEU.": "text",
    "On the WMT 2014 English-to-French translation task, the model established a new single-model state-of-the-art BLEU score of 41.8.": "text"
}


# Put it all together
def main():

    # Step 1: Extract text from PDF
    # text = pdf_to_text('paper-example.pdf')

    # Step 2: Convert text to script
    # script = text_to_script(text)

    # Step 3: Convert script to voice
    # voice_filename, audio  = text_to_voice(script)

    # Step 4: Convert script to animation
    animations = create_scene(script)

    # Step 5: Render video
    # render_vid(animations, 'output.wav')


if __name__ == "__main__":
    main()
