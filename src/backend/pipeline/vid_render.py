from functools import lru_cache
import logging
import os
from moviepy.editor import (
    AudioFileClip,
    ColorClip,
    VideoFileClip,
    ImageClip,
    concatenate_audioclips,
    concatenate_videoclips,
    CompositeVideoClip,
)
from moviepy.video.fx.all import mask_color
import re

from .constants import VIDEO_FPS
from .script import Script, TextScriptScene, for_every_scene
from .text_alignments_to_captions import CAPTION_COLOR_KEY
from .tmp import tmp_content_scene_dir_path, tmp_path, tmp_scene_sub_paths


@lru_cache(maxsize=None)
def get_files_from_directory(directory: str, file_patterns: list):
    """Lists all files matching the given patterns in a directory and its subdirectories."""
    matches = {file_pattern: [] for file_pattern in file_patterns}
    patterns = {
        file_pattern: re.compile(file_pattern) for file_pattern in file_patterns
    }
    for root, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            for file_pattern, pattern in patterns.items():
                if pattern.match(filename):
                    matches[file_pattern].append(os.path.join(root, filename))
    return matches


def hex_to_rgb(hex_color_string):
    hex_color_string = hex_color_string.lstrip("#")
    return [int(hex_color_string[i : i + 2], 16) for i in (0, 2, 4)]


def render_vid(paper_id, script: Script, output_filename: str):
    try:
        # Check if the output file already exists, if yes, return it
        if os.path.exists(output_filename):
            print(
                f"Video file {output_filename} already exists. Returning the existing file."
            )
            return output_filename

        def _process_scene(context: tuple[int, int], scene: TextScriptScene):
            section_id = context[0]
            scene_id = context[1]

            scene_dir_path = tmp_content_scene_dir_path(
                paper_id=paper_id, section_id=section_id, scene_id=scene_id
            )

            media_paths = get_files_from_directory(
                scene_dir_path, ["audio", "stock_footage", "caption_video"]
            )

            audio = AudioFileClip(media_paths["audio"][0])
            caption = VideoFileClip(media_paths["caption_video"][0], has_mask=True)
            stock_videos = [
                VideoFileClip(video) for video in media_paths["stock_footage"]
            ]

            single_stock_video = concatenate_videoclips(stock_videos, method="compose")
            single_stock_video = single_stock_video.resize(height=1080)

            caption = caption.subclip(0, single_stock_video.duration)
            caption = caption.set_fps(VIDEO_FPS)
            caption = caption.resize(height=1080)

            video = CompositeVideoClip([single_stock_video, caption])

            # Add a black clip with cross dissolve if audio is longer than video
            if audio.duration > video.duration:
                black_clip_duration = audio.duration - video.duration
                black_clip = ColorClip(
                    (1920, 1080), col=(0, 0, 0), duration=black_clip_duration
                )
                black_clip = black_clip.crossfadein(1).crossfadeout(
                    1
                )  # 1-second cross dissolve in and out
                video = concatenate_videoclips([video, black_clip], method="compose")
            else:
                video = video.set_duration(audio.duration)

            video = video.set_audio(audio)

            return video

        clips = for_every_scene(script, _process_scene)

        final_video = concatenate_videoclips(clips, method="compose")

        # Write the result to a file
        final_video.write_videofile(
            output_filename, codec="libx264", audio_codec="aac", fps=VIDEO_FPS
        )
    except Exception as e:
        logging.info("Failed to write video file")
        logging.info(e)
        raise e


if __name__ == "__main__":
    print(hex_to_rgb(CAPTION_COLOR_KEY), [1, 2, 3])
