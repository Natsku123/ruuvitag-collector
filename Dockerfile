FROM python:3.9-slim

LABEL maintainer="Max Mecklin <max@meckl.in>"

RUN apt-get update && \
    apt-get -y install gcc musl-dev python3-dev sudo bluez bluez-hcidump && \
    rm -rf /var/lib/apt/lists/*

COPY . /app

WORKDIR /app

RUN pip3.9 install -r requirements.txt

RUN pip3.9 install wheel
RUN pip3.9 install git+https://github.com/ttu/ruuvitag-sensor.git@migrate-rx-to-v3

CMD ["python3.9", "main.py"]