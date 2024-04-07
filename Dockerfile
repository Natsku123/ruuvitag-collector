FROM python:3.11-slim-buster

LABEL maintainer="Max Mecklin <max@meckl.in>"

RUN apt-get update && \
    apt-get -y --no-install-recommends install git gcc musl-dev python3-dev sudo bluez dbus bluez-hcidump && \
    rm -rf /var/lib/apt/lists/*

COPY . /app

WORKDIR /app

RUN pip3.11 install -r requirements.txt

RUN pip3.11 install wheel
RUN pip3.11 install git+https://github.com/ttu/ruuvitag-sensor.git

RUN ["chmod", "+x", "/docker-entrypoint.sh"]

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["python3.11", "main.py"]