import moviepy.editor as mp
import whisper
from datetime import timedelta
from docx import Document
from aiogram.types import FSInputFile

# Change to large MB
model_name = 'large'
model = whisper.load_model(model_name)


def convert(video_path, audio_path):
    clip = mp.VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path)


def recognize(source_file_name):
    audio = whisper.load_audio(f'./tmp/{source_file_name}.wav')
    audio = whisper.pad_or_trim(audio)
    mel = whisper.log_mel_spectrogram(audio=audio, n_mels=128).to(model.device)
    _, probs = model.detect_language(mel)
    result = model.transcribe(f'./tmp/{source_file_name}' + '.wav',)
    segments = result['segments']
    text_massive = []
    for segment in segments:
        startTime = str(0)+str(timedelta(seconds=int(segment['start'])))
        endTime = str(0)+str(timedelta(seconds=int(segment['end'])))
        text = segment['text']
        segmentId = segment['id']+1
        segment = f"{segmentId}. {startTime} - {endTime}\n{text[1:] if text[0] == ' ' else text}"
        text_massive.append(segment)
    text = text_massive
    doc = Document()
    for key in text:
        doc.add_paragraph(key)
    doc.save(f"./tmp/{source_file_name}.docx")

    return FSInputFile(f"./tmp/{source_file_name}.docx", filename="Транскрипция.docx")