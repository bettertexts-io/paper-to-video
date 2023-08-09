import os
from enum import Enum
from os.path import join, dirname
from dotenv import load_dotenv
from elevenlabs import generate, play, set_api_key, voices
from gtts import gTTS

from tmp import tmp_audio_path

class VOICE_PROVIDER(Enum):
    ELEVENLABS = "ELEVENLABS"
    GTTS = "GTTS"

def print_voices():
    available_voices = voices()

    print(available_voices)


def text_to_voice(paper_id: str, input: str, voice_provider = VOICE_PROVIDER.GTTS):
    if voice_provider == VOICE_PROVIDER.GTTS:
        tts = gTTS(input)
        tts.save(tmp_audio_path(paper_id))
    else:
        # Dotenv setup
        dotenv_path = join(dirname(__file__), '.env')
        load_dotenv(dotenv_path)

        set_api_key(os.environ.get("ELEVENLABS_API_KEY"))

        audio = generate(
            text=input,
            voice="W5xFSFFgg8Y0CKoTQ5n8",
            model="eleven_monolingual_v1"
        )

        # Assuming 'audio' is a byte stream
        with open(tmp_audio_path(paper_id), 'wb') as f:
            f.write(audio)


if __name__ == "__main__":
    filename = text_to_voice("1706.03762", "Write a video script for a short, informative, scientific video based on this scientific paper.")
