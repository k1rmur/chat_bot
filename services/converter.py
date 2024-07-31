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
    audio = whisper.pad_or_trim(audio)
    if model_name == 'large':
        mel = whisper.log_mel_spectrogram(audio=audio).to(model.device)
    elif model_name == 'tiny':
        mel = whisper.log_mel_spectrogram(audio=audio, n_mels=128).to(model.device)
    else:
        mel = whisper.log_mel_spectrogram(audio=audio, n_mels=80).to(model.device)

    _, probs = model.detect_language(mel)
    result = await loop.run_in_executor(None, functools.partial(model.transcribe, (f'./tmp/{file_id}' + '.wav',)))
    segments = result['segments']
    text_massive = []
    for segment in segments:
        text = segment['text']
        segment = f"{text[1:] if text[0] == ' ' else text}"
        text_massive.append(segment)
    text = text_massive

    return ' '.join(text)