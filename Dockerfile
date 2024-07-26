FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg

RUN curl -fsSL https://ollama.com/install.sh | sh

COPY run-ollama.sh .

RUN chmod +x run-ollama.sh \
    && ./run-ollama.sh

COPY . /app

CMD python get_bot.py