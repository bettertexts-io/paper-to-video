from typing import List, Tuple
import os
from enum import Enum
from os.path import dirname, join
import tempfile
import json


from dotenv import load_dotenv

from elevenlabs import generate, play, set_api_key, voices
from gtts import gTTS

from script import Script, ScriptSection, TextScriptScene, for_every_scene
from tmp import (
    create_directories_from_path,
    tmp_content_scene_dir_path,
    tmp_path,
    tmp_saver,
    tmp_scene_path,
)

import aeneas
from aeneas.executetask import ExecuteTask
from aeneas.task import Task

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

        set_api_key(os.environ.get("ELEVENLABS_API_KEY"))

        audio = generate(
            text=input,
            voice="W5xFSFFgg8Y0CKoTQ5n8",
            model="eleven_monolingual_v1"
        )

        # Assuming 'audio' is a byte stream
        with open(output_path, 'wb') as f:
            f.write(audio)

def generate_script_audio_pieces(paper_id: str, script: Script):
    def _process_scene(context: Tuple[int, int], scene: TextScriptScene):
            sceneDir = tmp_content_scene_dir_path(
                paper_id=paper_id, section_id=context[0], scene_id=context[1]
            )
            audio_path = tmp_scene_path(paper_id, context[0], context[1], "audio")
            alignment_path = tmp_scene_path(paper_id, context[0], context[1], "text_alignments")

            create_directories_from_path(sceneDir)

            if not os.path.exists(audio_path):
                text_to_voice(
                    paper_id=paper_id, input=scene["speakerScript"], output_path=audio_path
                )

            if not os.path.exists(alignment_path):
                align_audio_with_text(audio_path, scene["speakerScript"], alignment_path)

            return audio_path

    return for_every_scene(script, _process_scene)

def align_audio_with_text(audio_path, text_content, output_path):
    # Configuration string for the task
    config_string = "task_language=eng|os_task_file_format=json|is_text_type=plain"

    word_by_word_text = "\n".join(text_content.split())


    # Create a Task object
    task = Task(config_string=config_string)
    task.audio_file_path_absolute = audio_path

    # Create a temporary file to store the text content
    with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".txt") as temp_file:
        temp_file.write(word_by_word_text)
        text_file_path = temp_file.name

    task.text_file_path_absolute = text_file_path

    # Output file (can be deleted later if needed)
    task.sync_map_file_path_absolute = output_path

    # Process the task
    ExecuteTask(task).execute()
    task.output_sync_map_file()

    # Load the resulting alignment from the output JSON
    alignments = []
    with open(output_path, 'r') as f:
        data = json.load(f)
        for fragment in data['fragments']:
            start_time = float(fragment['begin'])
            end_time = float(fragment['end'])
            text_fragment = fragment['lines'][0]
            alignments.append((start_time, end_time, text_fragment))

    # Cleanup temp files
    os.remove(text_file_path)

    return alignments

if __name__ == "__main__":
    audio_file = "tmp/1706.03762/contentPieces/0/0/audio.mp3"
    speaker_script = "The paper 'Attention Is All You Need' introduces a new network architecture, the Transformer, which relies solely on attention mechanisms and does not use recurrent or convolutional neural networks."
    output_path = "tmp/1706.03762/contentPieces/0/0/audio_alignments.json"
    
    results = align_audio_with_text(audio_file, speaker_script, output_path)
    
    print(results)
