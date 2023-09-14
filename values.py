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
    ip = '10.10.11.118'
    port = 502


class Device:
    vebus = 227
    battery = 225


class Register:
    mode = 33
    soc = 266
