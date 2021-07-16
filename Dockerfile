FROM python:3.9-slim

LABEL maintainer="Max Mecklin <max@meckl.in>"

RUN apt-get update && \
    apt-get -y install gcc musl-dev python3-dev bluez-hcidump && \
    rm -rf /var/lib/apt/lists/*

COPY . /app

WORKDIR /app

RUN pip3.9 install -r requirements.txt

CMD ["python3.9", "main.py"]