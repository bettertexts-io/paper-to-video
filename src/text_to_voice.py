import os
from enum import Enum
from os.path import dirname, join

from dotenv import load_dotenv

# from elevenlabs import generate, play, set_api_key, voices
from gtts import gTTS

from script import Script, ScriptSection
from tmp import (
    create_directories_from_path,
    tmp_content_scene_dir_path,
    tmp_path,
    tmp_saver,
)


class VOICE_PROVIDER(Enum):
    ELEVENLABS = "ELEVENLABS"
    GTTS = "GTTS"


def print_voices():
    available_voices = voices()

    print(available_voices)


def text_to_voice(
    paper_id: str, input: str, output_path: str, voice_provider=VOICE_PROVIDER.GTTS
):
    if voice_provider == VOICE_PROVIDER.GTTS:
        tts = gTTS(input)
        tts.save(output_path)
    else:
        # Dotenv setup
        dotenv_path = join(dirname(__file__), ".env")
        load_dotenv(dotenv_path)

        # set_api_key(os.environ.get("ELEVENLABS_API_KEY"))

        # audio = generate(
        #     text=input,
        #     voice="W5xFSFFgg8Y0CKoTQ5n8",
        #     model="eleven_monolingual_v1"
        # )

        # # Assuming 'audio' is a byte stream
        # with open(output_path, 'wb') as f:
        #     f.write(audio)


def generate_script_audio_pieces(paper_id: str, script: Script):
    paths = []
    for section_id, section in enumerate(script["sections"]):
        for index, scene in enumerate(section["scenes"]):
            sceneDir = tmp_content_scene_dir_path(
                paper_id=paper_id, section_id=section_id, scene_id=index
            )
            create_directories_from_path(sceneDir)

            path = sceneDir + "/audio.mp3"
            if not os.path.exists(path):
                text_to_voice(
                    paper_id=paper_id, input=scene["speakerScript"], output_path=path
                )

            paths.append(path)

    return paths


if __name__ == "__main__":
    filename = text_to_voice(
        "1706.03762",
        "Write a video script for a short, informative, scientific video based on this scientific paper.",
    )
