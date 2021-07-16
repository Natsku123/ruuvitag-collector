FROM python:3.9-alpine

LABEL maintainer="Max Mecklin <max@meckl.in>"

COPY . /app

WORKDIR /app

RUN pip3.9 install -r requirements.txt

CMD ["python3.9", "main.py"]