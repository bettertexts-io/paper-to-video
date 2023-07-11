from concurrent.futures import ThreadPoolExecutor
from extract_paper import pdf_to_text
from text_to_script import text_to_script
from text_to_animation import create_scene
from text_to_voice import text_to_voice
from vid_render import render_vid

sample_script = {
    "This is a simple text scene": "text",
    "Integrate function from a to b": "mathtex",
    "This is a simple text scene": "text",
    "Integrate function from a to b": "mathtex",
    "This is a simple text scene": "text",
    "Integrate function from a to b": "mathtex",
    "This is a simple text scene": "text",
    "Integrate function from a to b": "mathtex",
}

# Put it all together
def main():

    # Step 1: Extract text from PDF
    text = pdf_to_text('paper-example.pdf')

    # Step 2: Convert text to script
    script = text_to_script(text)

    # Step 3: Convert script to animations
    # Step 4: Convert script to voice
    # Run these two in parallel
    with ThreadPoolExecutor(max_workers=2) as executor:
        animations_future = executor.submit(create_scene, sample_script)
        voice_future = executor.submit(text_to_voice, text)

    # Retrieve the results
    animations = animations_future.result()
    voice_filename, audio  = voice_future.result()

    # Step 5: Render video
    render_vid(animations, voice_filename)

if __name__ == "__main__":
    main()
