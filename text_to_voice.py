import os
from os.path import join, dirname
from dotenv import load_dotenv
from elevenlabs import generate, play, set_api_key, voices

# Dotenv setup
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

set_api_key(os.environ.get("ELEVENLABS_API_KEY"))

def print_voices():
    available_voices = voices()

    print(available_voices)


def text_to_voice(text, filename="output.wav"):
    audio = generate(
        text=text,
        voice="W5xFSFFgg8Y0CKoTQ5n8",
        model="eleven_monolingual_v1"
    )

    # Assuming 'audio' is a byte stream
    with open(filename, 'wb') as f:
        f.write(audio)

    return filename, audio

filename, audio = text_to_voice("Write a video script for a short, informative, scientific video based on this scientific paper.")
play(audio)
