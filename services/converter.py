import os
import glob
import whisper
import asyncio
import functools

model_name = 'medium'
model = whisper.load_model(model_name)


def clear_temp():
    files = glob.glob('./tmp/*')
    for f in files:
        os.remove(f)


async def recognize(file_id):
    loop = asyncio.get_event_loop()
    audio = whisper.load_audio(f'./tmp/{file_id}.wav')

    result = await loop.run_in_executor(None, functools.partial(model.transcribe, audio, language='ru'))
    segments = result['segments']
    text_massive = []
    for segment in segments:
        text = segment['text']
        segment = f"{text[1:] if text[0] == ' ' else text}"
        text_massive.append(segment)
    text = text_massive

    return ' '.join(text)