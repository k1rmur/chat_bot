FROM python:3.10

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install --no-cache-dir --ignore-installed -r requirements.txt

RUN pip install llama-cpp-python --prefer-binary --no-cache-dir --extra-index-url=https://jllllll.github.io/llama-cpp-python-cuBLAS-wheels/AVX2/cpu/
