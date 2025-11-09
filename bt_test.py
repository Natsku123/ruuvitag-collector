import logging
import signal

import asyncio
from datetime import datetime
from multiprocessing import Manager
from concurrent.futures import ProcessPoolExecutor

from ruuvitag_sensor.ruuvi import RuuviTagSensor

import ruuvitag_sensor.log

ruuvitag_sensor.log.enable_console()
ruuvitag_sensor.log.log.setLevel(logging.DEBUG)

sensors = ["F5:DB:67:37:D0:F6", "DB:B8:35:4E:77:77", "CC:4E:E4:36:9C:97", "FC:CF:09:35:0C:0A", "FE:C1:1B:EB:4A:68"]


def handle_sigterm(sig, frame):
    raise KeyboardInterrupt


signal.signal(signal.SIGTERM, handle_sigterm)


async def handle_data(received_data: dict):
    """
    Handle data from a Ruuvi tag and send it to InfluxDB.

    :param received_data:
    :return:
    """
    payload = received_data['data']
    ruuvitag_sensor.log.log.info(f"Received from {received_data['mac']}.")
    ruuvitag_sensor.log.log.debug(f"Payload: {payload}")


async def handle_queue(queue):
    try:
        while True:
            if not queue.empty():
                funcs = []
                while not queue.empty():
                    update_data = queue.get()
                    funcs.append(asyncio.create_task(handle_data(update_data)))

                if funcs:
                    await asyncio.wait(funcs)
            else:
                await asyncio.sleep(0.2)
    except KeyboardInterrupt:
        ruuvitag_sensor.log.log.info("Shutting down...")


def background_process(queue):
    def handle_new_data(new_data):
        current_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        sensor_mac = new_data[0]
        sensor_data = new_data[1]

        update_data = {'mac': sensor_mac, 'data': sensor_data,
                       'timestamp': current_time}
        queue.put(update_data)

    RuuviTagSensor.get_data(handle_new_data, macs=sensors)


def main():

    ruuvitag_sensor.log.log.info("Starting...")
    m = Manager()
    q = m.Queue()

    executor = ProcessPoolExecutor()
    executor.submit(background_process, q)

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()

    ruuvitag_sensor.log.log.info("Started listening for data...")
    loop.run_until_complete(handle_queue(q))

if __name__ == "__main__":
    main()
