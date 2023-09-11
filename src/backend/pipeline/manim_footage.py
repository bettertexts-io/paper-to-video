import os
import subprocess
import openai
import json
from manim import *

from .constants import OPENAI_API_KEY


def extract_code(content):
    # Assuming the response is a string with Python code for now.
    # For a more complex response structure, we'd need to parse the content accordingly.
    return content


def extract_construct_code(code_content):
    # For now, we're assuming that the response directly gives the Manim code inside the construct method.
    return code_content


def code_static_corrector(code_content):
    # For now, this function doesn't change the code.
    # Later, you can add any specific corrections you may need.
    return code_content


def create_file_content(code_content):
    # Boilerplate code for Manim with our provided scene code.
    template = """
    from manim import *

    class GenScene(Scene):
        def construct(self):
            {0}
    """
    return template.format(code_content)


def generate_animation(paper_id, script_with_scenes):
    script = json.loads(script_with_scenes)
    sections = script["sections"]

    for section in sections:
        title = section["title"]
        context = section["context"]
        scenes = section["scenes"]

        for idx, scene in enumerate(scenes):
            if scene["type"] == "TEXT":
                prompt = scene["manimQuery"]

                # Make API call
                response = openai.Completion.create(
                    model="gpt-4.0-turbo",
                    prompt=prompt,
                )

                # Extract and correct code
                code_response = extract_construct_code(
                    extract_code(response.choices[0].message.content)
                )
                code_response = code_static_corrector(code_response)

                # Name of the file based on the title and scene number
                filename = f"GenScene_{title.replace(' ', '_')}_{idx}.py"

                # Write to file
                with open(filename, "w") as f:
                    f.write(create_file_content(code_response))

                # Render using manim
                COMMAND_TO_RENDER = f"manim {filename} GenScene --format=mp4 --media_dir . --custom_folders video_dir"
                try:
                    subprocess.run(COMMAND_TO_RENDER, check=True, shell=True)
                except Exception as e:
                    print(f"Error while rendering scene {idx} from {title}: ", e)

    print("All animations generated.")


if __name__ == "__main__":
    # Example use case
    print("Generating animations...")
