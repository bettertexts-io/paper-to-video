import json
import os
import re
import textwrap
from typing import List, Tuple
from manim import *
from script import TextScriptScene, for_every_scene
from tmp import tmp_content_scene_dir_path, tmp_scene_path, tmp_scene_sub_paths
from script import Script

CAPTION_COLOR_KEY = "#00FF00"

class SmallGrowFromCenter(GrowFromCenter):
    def interpolate_mobject(self, alpha: float) -> None:
        scale_factor = self.scale_factor_interpolation(alpha)
        self.mobject.become(self.starting_mobject)
        self.mobject.scale(scale_factor * 0.1)  # Adjust this value to change the growth amount


class WordOverlay(Scene):
    def __init__(self, paper_id, section_id, scene_id):
        super().__init__()
        self.paper_id = paper_id
        self.section_id = section_id
        self.scene_id = scene_id

    def construct(self):
        paper_id = self.paper_id
        section_id = self.section_id
        scene_id = self.scene_id

        alignment_path = tmp_scene_path(paper_id, section_id, scene_id, "text_alignments")

        with open(alignment_path, 'r') as f:
            data = json.load(f)
        
        for i, fragment in enumerate(data['fragments']):
            start_time = float(fragment['begin'])
            end_time = float(fragment['end'])
            text_fragment = fragment['lines'][0]
            text_fragment = text_fragment.strip()  # remove leading and trailing whitespaces
            text_fragment = re.sub(r'^\W+|\W+$', '', text_fragment)  # remove non-alphanumeric characters at the start and end of the string
            text_fragment = text_fragment.upper() 

            if end_time - start_time == 0:
                continue

            if i == 0 and start_time > 0:
                self.wait(start_time)

            if i == len(data['fragments']) - 1:
                wait_duration = 2
            else:
                next_fragment = data['fragments'][i + 1]
                wait_duration = float(next_fragment['begin']) - start_time

            print(text_fragment)
            
            texts = []
            if(text_fragment != ""):
                lines = textwrap.wrap(text_fragment, width=18)  # adjust width as needed
                texts = [Text(line, font="Sans Serif", font_size=70, stroke_width=8, stroke_color=BLACK, weight=BOLD, warn_missing_font=False).move_to(ORIGIN - i*(UP + 0.2)) for i, line in enumerate(lines)]
                self.play(*[Write(text) for text in texts], run_time=0.1)

            if wait_duration > 0.1:
                self.wait(wait_duration - 0.1)  # wait for the next word

            self.remove(*texts)
            

def generate_scene_captions(context: Tuple[int, int], paper_id: str):
        section_id = context[0]
        scene_id = context[1]
        output_path = tmp_scene_path(paper_id, context[0], context[1], "caption_video")
        print("context " + str(context))

        if os.path.exists(output_path):
            return output_path

        from manim import config
        config.frame_rate = 24
        config.output_file = output_path
        config.transparent = True
        config.format = "mov"
        config.resolution = (3840, 2160)  # Set resolution to 4K


        SceneClass = WordOverlay
        scene = SceneClass(paper_id=paper_id, section_id=section_id, scene_id=scene_id)
        scene.render()

        return output_path

def generate_video_captions(paper_id: str, script: Script):
    def _generate_scene_captions(context: Tuple[int, int], scene: TextScriptScene):
        return generate_scene_captions(context, paper_id)

    return for_every_scene(script, _generate_scene_captions)


# if __name__ == "__main__":
#     generate_scene_captions("1706.03762", 0, 0)