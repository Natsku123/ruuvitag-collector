FROM python:3.8-slim

LABEL maintainer="Max Mecklin <max@meckl.in>"

RUN apt-get update && \
    apt-get -y install gcc musl-dev python3-dev sudo bluez bluez-hcidump && \
    rm -rf /var/lib/apt/lists/*

COPY . /app

WORKDIR /app

RUN pip3.8 install -r requirements.txt

CMD ["python3.9", "main.py"]