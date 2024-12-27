import asyncio
import glob
import os

import moviepy.editor as mp
from docx import Document
from dotenv import find_dotenv, load_dotenv
from pydub import AudioSegment

load_dotenv(find_dotenv())


def change_speaker_name(string: str | None):
    if string is None:
        return "Собеседник"
    else:
        spk, num = string.split("_")
        num = int(num) + 1
    return f"Собеседник {num}"


HF_TOKEN = os.getenv("HF_TOKEN")


def clear_temp(file_id):
    files = glob.glob("./tmp/*")
    for f in files:
        if file_id in f:
            print(f"Deleting {f}...")
            os.remove(f)
    files = glob.glob("app/bot/tmp/*")
    for f in files:
        if file_id in f:
            print(f"Deleting {f}...")
            os.remove(f)


def is_video(extension):
    extention_list = ["webm", "mp4", "mkv", "flv", "avi", "mov", "wmv", "m4v"]

    return extension.lower() in extention_list


def is_audio(extension):
    extension_list = [
        "mp3",
        "oga",
        "ogg",
        "mogg",
        "3gp",
        "aac",
        "aa",
        "aax",
        "m4a",
        "mpc",
        "wav",
    ]

    return extension.lower() in extension_list


def convert(video_path, audio_path):
    clip = mp.VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path, ffmpeg_params=["-ac", "1"])


lock = asyncio.Lock()


def salute_recognize(file_id: str, extension: str):
    audio_path = f"/app/bot/tmp/{file_id}.{extension}"

    if extension not in ["mp3", "wav"]:
        song = AudioSegment.from_ogg(f"/app/bot/tmp/{file_id}.{extension}")
        song.export(f"/app/bot/tmp/{file_id}.wav", format="wav")

        audio_path = f"/app/bot/tmp/{file_id}.wav"

    text_file = f"./tmp/{file_id}.txt"
    os.system(f'salute_speech transcribe-audio "{audio_path}" -o "{text_file}"')

    doc_transcription = Document()

    with open(text_file, "r") as file:
        full_transcript = "\n".join(file.readlines())
        doc_transcription.add_paragraph(full_transcript)

    doc_transcription.save(f"./tmp/{file_id}.docx")

    return f"./tmp/{file_id}.docx", "Транскрипция.docx", full_transcript
