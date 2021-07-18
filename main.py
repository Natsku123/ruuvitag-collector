import os
import signal

import asyncio
from datetime import datetime
from multiprocessing import Manager
from concurrent.futures import ProcessPoolExecutor


from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import ASYNCHRONOUS

from ruuvitag_sensor.ruuvi import RuuviTagSensor

import ruuvitag_sensor.log

ruuvitag_sensor.log.enable_console()

sensors = os.environ.get('SENSORS', '')\
    .removeprefix('"').removesuffix('"').split(" ")

client = InfluxDBClient.from_env_properties()

bucket = os.environ.get('BUCKET', 'Ruuvi')


all_data = {}


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

    # Create a new point with tags for the device and data format
    # Get data from data and insert into point
    p = Point("temperature").tag("device", received_data['mac'])\
        .tag("data_format", payload.get('data_format'))\
        .field("temperature", payload.get('temperature'))\
        .field("humidity", payload.get('humidity'))\
        .field("pressure", payload.get('pressure'))\
        .field("accelerationX", payload.get('acceleration_x'))\
        .field("accelerationY", payload.get('acceleration_y'))\
        .field("accelerationZ", payload.get('acceleration_z'))\
        .field("batteryVoltage", payload.get('battery', 0)/1000.0)\
        .field("txPower", payload.get('tx_power'))\
        .field("movementCounter", payload.get('movement_counter'))\
        .field("measurementSequenceNumber", payload.get('measurement_sequence_number'))\
        .field("tagID", payload.get('tagID'))\
        .field("rssi", payload.get('rssi'))\
        .field("time", received_data.get('timestamp', datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')))
    # Send data to InfluxDB
    with client.write_api(write_options=ASYNCHRONOUS) as write_api:
        res = write_api.write(bucket=bucket, record=p)
        res.get()


async def handle_queue(queue):
    try:
        while True:
            if not queue.empty():
                funcs = []
                while not queue.empty():
                    update_data = queue.get()
                    funcs.append(handle_data(update_data))
                    if len(funcs) > 50:
                        break
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

        if sensor_mac not in all_data or \
                all_data[sensor_mac]['data'] != sensor_data:
            update_data = {'mac': sensor_mac, 'data': sensor_data,
                           'timestamp': current_time}
            all_data[sensor_mac] = update_data
            queue.put(update_data)
    RuuviTagSensor.get_datas(handle_new_data, macs=sensors)


if __name__ == "__main__":
    m = Manager()
    q = m.Queue()

    executor = ProcessPoolExecutor()
    executor.submit(background_process, q)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(handle_queue(q))
