import requests
from decouple import config
WATER_SENSOR_POWER_ON_OFF = "V0"
RAIN_SENSOR_POWER_ON_OFF = "V1"
WATER_SENSOR_VALUE = "V4"
WATER_SENSOR_TEXT_VALUE = "V5"
RAIN_SENSOR_VALUE = "V6"
RAIN_SENSOR_TEXT_VALUE = "V7"
RAIN_GAUGE_VALUE = "V8"
WATER_NOTIFICATION = "V9"
BLYNK_AUTH_TOKEN = config('BLYNK_AUTH_TOKEN')


def water_sensor_data_api():
    response = requests.get(
        f"https://blynk.cloud/external/api/get?token={BLYNK_AUTH_TOKEN}&{WATER_SENSOR_VALUE}"
    )
    if response.status_code == 200:
        data = response.json()
        return data


def rain_sensor_data_api():
    response = requests.get(
        f"https://blynk.cloud/external/api/get?token={BLYNK_AUTH_TOKEN}&{RAIN_SENSOR_VALUE}"
    )
    if response.status_code == 200:
        data = response.json()
        return data


def rain_gauge_data_api():
    response = requests.get(
        f"https://blynk.cloud/external/api/get?token={BLYNK_AUTH_TOKEN}&{RAIN_GAUGE_VALUE}"
    )
    if response.status_code == 200:
        data = response.json()
        return data


def water_sensor_text_data_api():
    response = requests.get(
        f"https://blynk.cloud/external/api/get?token={BLYNK_AUTH_TOKEN}&{WATER_SENSOR_TEXT_VALUE}"
    )
    if response.status_code == 200:
        data = response.text
        return data


def rain_sensor_text_data_api():
    response = requests.get(
        f"https://blynk.cloud/external/api/get?token={BLYNK_AUTH_TOKEN}&{RAIN_SENSOR_TEXT_VALUE}"
    )
    if response.status_code == 200:
        data = response.text
        return data


def water_notification_data_api():
    response = requests.get(
        f"https://blynk.cloud/external/api/get?token={BLYNK_AUTH_TOKEN}&{WATER_NOTIFICATION}"
    )
    if response.status_code == 200:
        data = response.text
        return data


def device_is_connected():
    response = requests.get(
        f"https://blynk.cloud/external/api/isHardwareConnected?token={BLYNK_AUTH_TOKEN}"
    )
    if response.status_code == 200:
        data = response.json()
        return data
