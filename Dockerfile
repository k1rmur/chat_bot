FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg

COPY . /app

RUN sh -c "pip install protobuf==3.19.4 && cp ./builder.py /usr/local/lib/python3.10/site-packages/google/protobuf/internal/"

RUN python make_embeddings.py --Mode outer

RUN python make_embeddings.py --Mode inner