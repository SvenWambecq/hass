from dsmr_parser import telegram_specifications
from dsmr_parser.clients import SerialReader, SERIAL_SETTINGS_V5


SPECIFICATION = telegram_specifications.BELGIUM_FLUVIUS

serial_reader = SerialReader(
    device='/dev/ttyUSB0',
    serial_settings=SERIAL_SETTINGS_V5,
    telegram_specification=SPECIFICATION
)

from requests import post
import time

SENSORS = {
    "water_meter": {
        "id": "BELGIUM_MBUS2_METER_READING1",
        "device_class": "water",
        "state_class": "total_increasing"
    },
    "gas_verbruik": {
        "id": "BELGIUM_MBUS1_METER_READING2",
        "device_class": "gas",
        "state_class": "total_increasing"
    },
    "max_demand_month": {
        "id": "BELGIUM_MAXIMUM_DEMAND_MONTH",
        "device_class": "power",
        "state_class": "total_increasing"
    },
    "current_average_demand": {
        "id": "BELGIUM_CURRENT_AVERAGE_DEMAND",
        "device_class": "power",
        "state_class": "measurement"
    },
    "electricity_used_tariff_1": {
        "id": "ELECTRICITY_USED_TARIFF_1",
        "device_class": "energy",
        "state_class": "total_increasing"
    },
    "electricity_used_tariff_2": {
        "id": "ELECTRICITY_USED_TARIFF_2",
        "device_class": "energy",
        "state_class": "total_increasing"
    },
    "electricity_delivered_tariff_1": {
        "id": "ELECTRICITY_DELIVERED_TARIFF_1",
        "device_class": "energy",
        "state_class": "total_increasing"
    },
    "electricity_delivered_tariff_2": {
        "id": "ELECTRICITY_DELIVERED_TARIFF_2",
        "device_class": "energy",
        "state_class": "total_increasing"
    }
}

def dimension(v):
    if v == "m3":
        return "m³"
    else:
        return v

BASE_URL = "http://localhost:8123/api/states/sensor.{sensor}"
TOKEN = "TOKEN"
HEADER = {"Authorization": f"Bearer {TOKEN}",  "content-type": "application/json"}

for telegram in serial_reader.read():
    #print(telegram)
    for sensor, d in SENSORS.items():
        measurement = getattr(telegram, d["id"])
        data = {
            "state": str(measurement.value), 
            "attributes": {
                "unit_of_measurement":  dimension(measurement.unit), 
                "device_class": d["device_class"], 
                "state_class": d["state_class"]
            }
        }
        url = BASE_URL.format(sensor=sensor)
        try: 
            response = post(url, headers=HEADER, json=data)
            print(response.text)
        except Exception:
            pass
