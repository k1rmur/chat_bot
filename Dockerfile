FROM python:3.10

COPY . .

RUN pip install --upgrade pip setuptools

RUN pip install --no-cache-dir --ignore-installed -r requirements.txt
