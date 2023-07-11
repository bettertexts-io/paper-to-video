from moviepy.editor import concatenate_videoclips, AudioFileClip, VideoFileClip, ColorClip
from moviepy.video.fx import all as fx

def render_vid(animations, voice, output='output.mp4'):
    # Load the animations and the voice
    clips = [VideoFileClip(animation) for animation in animations]
    audio = AudioFileClip(voice)

    # Calculate total duration of video clips and audio clip
    video_duration = sum(clip.duration for clip in clips)
    audio_duration = audio.duration

    # Add a black clip with cross dissolve if audio is longer than video
    if audio_duration > video_duration:
        black_clip = ColorClip((1920, 1080), col=(0,0,0), duration=audio_duration - video_duration)
        black_clip = black_clip.crossfadein(1).crossfadeout(1)  # 1 second cross dissolve in and out
        clips.append(black_clip)

    # Concatenate all video clips
    final_clip = concatenate_videoclips(clips)

    # Set the audio of the final clip to the voice
    final_clip = final_clip.set_audio(audio)

    # Write the result to a file (many options available !)
    final_clip.write_videofile(output, codec='libx264', audio_codec='aac')

# Use the function
render_vid(['example-scene.mp4'], 'output.wav')
