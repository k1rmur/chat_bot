import os
import glob
import torch
import moviepy.editor as mp
from docx import Document
from pyannote.audio import Pipeline
from dotenv import load_dotenv, find_dotenv
import asyncio
import functools
import whisperx


load_dotenv(find_dotenv())

def change_speaker_name(string: str | None):
    if string is None:
        return "Собеседник"
    else:
        spk, num = string.split('_')
        num = int(num)+1
    return f'Собеседник {num}'


HF_TOKEN = os.getenv('HF_TOKEN')


device = "cuda" if torch.cuda.is_available() else "cpu"
print(device)
compute_type = "int8"
batch_size = 16

model_dir = "/app/bot/services/models/"
model_name = 'medium'

model = whisperx.load_model(model_name, device=device, compute_type=compute_type, download_root=model_dir, language='ru')


async def recognize_voice(file_id):
    audiofile = f'./tmp/{file_id}.wav'
    loop = asyncio.get_event_loop()
#    audio = whisperx.load_audio(audiofile)

    result = await loop.run_in_executor(None, functools.partial(model.transcribe, audiofile, language='ru', batch_size=batch_size))
    segments = result['segments']
    text_massive = []
    for segment in segments:
        text = segment['text']
        segment = f"{text[1:] if text[0] == ' ' else text}"
        text_massive.append(segment)
    text = text_massive

    return ' '.join(text)


def is_video(extension):
    extention_list = [
        "webm",
        "mp4",
        "mkv",
        "flv",
        "avi",
        "mov",
        "wmv",
        "m4v"
    ]

    return extension.lower() in extention_list


def is_audio(extension):
    extension_list = [
        "mp3",
        "oga",
        "ogg",
        "mogg"
        "3gp",
        "aac",
        "aa",
        "aax",
        "m4a",
        "mpc",
        "wav"
    ]

    return extension.lower() in extension_list


def convert(video_path, audio_path):
    clip = mp.VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path, ffmpeg_params=["-ac", "1"])


async def recognize(file_id, extension):
    loop = asyncio.get_event_loop()
    audiofile = f'./tmp/{file_id}.{extension}'
    audio = whisperx.load_audio(audiofile)
    transcription_result = await loop.run_in_executor(None, functools.partial(model.transcribe, audiofile, language='ru', batch_size=batch_size))
    model_a, metadata = whisperx.load_align_model(language_code='ru', device=device)
    result = await loop.run_in_executor(None, functools.partial(whisperx.align, transcription_result["segments"], model_a, metadata, audio, device, return_char_alignments=False))
    diarize_model = whisperx.DiarizationPipeline(use_auth_token=HF_TOKEN, device=device)
    diarize_segments = await loop.run_in_executor(None, functools.partial(diarize_model, audio))
    result = whisperx.assign_word_speakers(diarize_segments, result)

    text_for_summary = []
    doc_transcription = Document()

    for segment in result["segments"]:
        speaker = change_speaker_name(segment.get("speaker"))
        line_massive = f"[{segment.get('start'):.3f} --> {segment.get('end'):.3f}] {speaker}: {segment.get('text')}"
        line_summary = f"{speaker}: {segment.get('text')}\n"
        text_for_summary.append(line_summary)
        doc_transcription.add_paragraph(line_massive)


    doc_transcription.save(f"./tmp/{file_id}.docx")

    return f"./tmp/{file_id}.docx", "Транскрипция.docx", '\n'.join(text_for_summary)


def clear_temp():
    files = glob.glob('./tmp/*')
    for f in files:
        os.remove(f)