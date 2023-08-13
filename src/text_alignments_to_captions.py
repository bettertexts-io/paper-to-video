import json
import os
import re
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
            text_fragment = re.sub(r'\W+', '', text_fragment)  # remove all non-alphanumeric characters
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

            print(f"Fragment {i}: {text_fragment} ({start_time} - {end_time}) {wait_duration}")

            text = Text(text_fragment).move_to(ORIGIN) 
            self.play(Write(text), run_time=0.1)  # animate the word
            self.wait(wait_duration - 0.1)  # wait for the next word
            self.remove(text)

def generate_scene_captions(context: Tuple[int, int], paper_id: str):
        section_id = context[0]
        scene_id = context[1]
        output_path = tmp_scene_path(paper_id, context[0], context[1], "caption_video")

        if os.path.exists(output_path):
            return output_path

        from manim import config
        config.frame_rate = 24
        config.output_file = output_path
        config.transparent = True
        config.format = "gif"

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