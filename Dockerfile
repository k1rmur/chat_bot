FROM ubuntu:latest

RUN groupadd -g 2000 appgroup && \
    useradd -u 2000 -g appgroup -m -s /bin/bash appuser

RUN apt update && \
    apt install -y python3 python3-pip python3-venv

RUN mkdir /app && \
    chown -R appuser:appgroup /app /var /run && \
    chmod -R 755 /app

WORKDIR /app
RUN python3 -m venv venv

ENV PATH="/app/venv/bin:$PATH"
RUN . venv/bin/activate

COPY . .

RUN pip install --ignore-installed --no-cache-dir -r requirements.txt --default-timeout=100

USER root

CMD ["./venv/bin/python3", "make_embeddings.py", "&&", "./venv/bin/python3", "get_bot.py"]

