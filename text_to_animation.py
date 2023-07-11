from manim import *
from manim import config

class TextScene(Scene):
    def __init__(self, text):
        super().__init__()
        self.text = text

    def construct(self):
        text_obj = Text(self.text)
        self.play(Write(text_obj))
        self.wait(2)

class MathTexScene(Scene):
    def __init__(self, equation):
        super().__init__()
        self.equation = equation

    def construct(self):
        equation_obj = MathTex(self.equation)
        self.play(Write(equation_obj))
        self.wait(2)

# Mapping of annotation to scene
scene_dict = {
    "text": TextScene,
    "mathtex": MathTexScene
}

def create_scene(input_script):
    output_files = []
    for sentence, annotation in input_script.items():
        if annotation in scene_dict:
            SceneClass = scene_dict[annotation]
            scene = SceneClass(sentence)

            # set custom output file name
            output_file = f"{sentence.replace(' ', '_')}.mp4"  
            config['output_file'] = output_file

            scene.render()  # Manim renders the scene upon calling this method

            # Add generated mp4 file to the list
            output_files.append(output_file)
            
        else:
            print(f"No scene found for annotation {annotation}")

    return output_files

# Example usage
script = {
    "This is a simple text scene": "text",
    "Integrate function from a to b": "mathtex"
}

print(create_scene(script))
