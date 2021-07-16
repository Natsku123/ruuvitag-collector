import os

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from ruuvitag_sensor.ruuvi import RuuviTagSensor

import ruuvitag_sensor.log

ruuvitag_sensor.log.enable_console()

sensors = os.environ.get('SENSORS', '').split(" ")

client = InfluxDBClient.from_env_properties()

bucket = os.environ.get('BUCKET', 'Ruuvi')


def handle_data(received_data):
    """
    Handle data from a Ruuvi tag and send it to InfluxDB.

    :param received_data:
    :return:
    """
    mac = received_data[0]
    payload = received_data[1]

    # Create a new point with tags for the device and data format
    # Get data from data and insert into point
    p = Point("temperature").tag("device", mac)\
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
        .field("rssi", payload.get('rssi'))

    # Send data to InfluxDB
    with client.write_api(write_options=SYNCHRONOUS) as write_api:
        write_api.write(bucket=bucket, record=p)


if __name__ == "__main__":
    RuuviTagSensor.get_datas(handle_data, macs=sensors)
