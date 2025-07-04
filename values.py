import os


class Mode:
    value = {
        "Charger Only": 1,
        "Inverter Only": 2,
        "On": 3,
        "Off": 4
    }

    name = {
        1: "Charger Only",
        2: "Inverter Only",
        3: "On",
        4: "Off"
    }


class Host:
    ip = os.getenv('MODBUS_HOST')
    port = int(os.getenv('MODBUS_PORT')) if os.getenv('MODBUS_PORT') else 502


class Device:
    vebus = 227
    battery = 225


class Register:
    mode = 33
    soc = 266


class Battery:
    high_connect_to_grid_above = 95
    high_disconnect_from_grid_below = 90
    low_connect_to_grid_below = 15
    low_disconnect_from_grid_above = 20


class Common:
    log_level = os.getenv('LOG_LEVEL') if os.getenv('LOG_LEVEL') else 'INFO'
    update_interval = int(os.getenv('UPDATE_INTERVAL')) if os.getenv('UPDATE_INTERVAL') else 60
    log_capacity = int(os.getenv('LOG_CAPACITY')) if os.getenv('LOG_CAPACITY') else 10000
