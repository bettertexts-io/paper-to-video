import json
import os
from typing import List, Tuple
from manim import *
from script import TextScriptScene, for_every_scene
from tmp import tmp_content_scene_dir_path, tmp_scene_path, tmp_scene_sub_paths
from script import Script

CAPTION_COLOR_KEY = "#00FF00"

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

            if end_time - start_time < 0.1:
                continue

            text = Text(text_fragment).move_to(ORIGIN) 
            self.play(Write(text), run_time=end_time - start_time)  # animate the word
            self.wait(start_time - end_time)
            self.remove(text)

def generate_video_captions(paper_id: str, script: Script):
    def generate_scene_captions(context: Tuple[int, int], scene: TextScriptScene):
        section_id = context[0]
        scene_id = context[1]
        output_path = tmp_scene_path(paper_id, context[0], context[1], "caption_video")

        if os.path.exists(output_path):
            return output_path

        from manim import config
        config.background_color = CAPTION_COLOR_KEY # Set the background color
        config.frame_rate = 24
        config.output_file = output_path

        SceneClass = WordOverlay
        scene = SceneClass(paper_id=paper_id, section_id=section_id, scene_id=scene_id)
        scene.render()

        return output_path


    return for_every_scene(script, generate_scene_captions)


# if __name__ == "__main__":
#     generate_scene_captions("1706.03762", 0, 0)