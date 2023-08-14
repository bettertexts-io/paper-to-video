from moviepy.editor import (
    AudioFileClip,
    ColorClip,
    VideoFileClip,
    concatenate_audioclips,
    concatenate_videoclips,
    CompositeVideoClip
)
from moviepy.video.fx.all import mask_color

from constants import VIDEO_FPS
from text_alignments_to_captions import CAPTION_COLOR_KEY

def hex_to_rgb(hex_color_string):
    hex_color_string = hex_color_string.lstrip('#')
    return [int(hex_color_string[i:i+2], 16) for i in (0, 2, 4)]

def render_vid(
    animation_filenames: list[str], voice_filenames: list[str], output_filename: str, video_caption_filenames: list[str]
):
    # Load the animations and the voice
    videos = [VideoFileClip(animation) for animation in animation_filenames]
    audios = [AudioFileClip(voice) for voice in voice_filenames]
    captions = [VideoFileClip(caption, has_mask=True) for caption in video_caption_filenames]

    for i, video in enumerate(videos):
        video.set_fps(VIDEO_FPS)
        video.duration = audios[i].duration  # Sync video duration with audio

        captions[i].set_fps(VIDEO_FPS)
        captions[i] = captions[i].subclip(0, video.duration)  # Sync caption duration with video
        print(captions[i].get_frame(0)[0][0])

        videos[i] = CompositeVideoClip([video, captions[i]])

    total_audio_duration = sum(clip.duration for clip in audios)
    total_video_duration = sum(clip.duration for clip in videos)

    # Add a black clip with cross dissolve if audio is longer than video
    if total_audio_duration > total_video_duration:
        black_clip_duration = total_audio_duration - total_video_duration
        black_clip = ColorClip((1920, 1080), col=(0, 0, 0), duration=black_clip_duration)
        black_clip = black_clip.crossfadein(1).crossfadeout(1)  # 1-second cross dissolve in and out
        videos.append(black_clip)

    concatenated_video = concatenate_videoclips(videos, method="compose")
    concatenated_audio = concatenate_audioclips(audios)
    final_video = concatenated_video.set_audio(concatenated_audio)
    final_video.duration = total_audio_duration 

    # Write the result to a file
    final_video.write_videofile(output_filename, codec="libx264", audio_codec="aac", fps=VIDEO_FPS)

if __name__ == "__main__":
    print(hex_to_rgb(CAPTION_COLOR_KEY), [1,2,3])
