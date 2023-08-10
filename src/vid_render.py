from moviepy.editor import (
    AudioFileClip,
    ColorClip,
    VideoFileClip,
    concatenate_audioclips,
    concatenate_videoclips,
)
from moviepy.video.fx import all as fx


def render_vid(
    animation_filenames: list[str], voice_filenames: list[str], output_filename: str
):
    # Load the animations and the voice
    videos = [VideoFileClip(animation) for animation in animation_filenames]
    audios = [AudioFileClip(voice) for voice in voice_filenames]

    for i in range(len(videos)):
        videos[i].duration = audios[i].duration
        videos[i].set_fps(24)

    # Calculate total duration of video videos and audio clip
    if len(videos) != 0:
        video_duration = sum(clip.duration for clip in videos)
    else:
        video_duration = 0

    if len(audios) != 0:
        audio_duration = sum(clip.duration for clip in audios)
    else:
        audio_duration = 0

    # Add a black clip with cross dissolve if audio is longer than video
    if audio_duration > video_duration:
        black_clip = ColorClip(
            (1920, 1080), col=(0, 0, 0), duration=audio_duration - video_duration
        )
        black_clip = black_clip.crossfadein(1).crossfadeout(
            1
        )  # 1 second cross dissolve in and out
        videos.append(black_clip)

    final_duration = audio_duration

    # Concatenate all video videos
    concatenated_video = concatenate_videoclips(videos, method="compose")
    concatenated_audio = concatenate_audioclips(audios)

    # Set the audio of the final clip to the voice
    final_video = concatenated_video.set_audio(concatenated_audio)

    # Write the result to a file (many options available !)
    # TODO: Check codex and audio encoding
    final_video.set_duration(final_duration)
    final_video.write_videofile(
        output_filename, codec="libx264", audio_codec="aac", fps=30
    )


# Use the function
if __name__ == "__main__":
    print()
    # render_vid(["animation1.mp4", "animation2.mp4"], ["voice1.mp3", "voice2.mp3"], "output.mp4")
