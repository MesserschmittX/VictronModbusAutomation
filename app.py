import time
import threading
from datetime import datetime
from pymodbus.client import ModbusTcpClient
from flask import Flask

from values import Mode, Device, Register, Host, Common

app = Flask(__name__)

# variables that are accessible from anywhere
common_data_struct = {}
last_seen = datetime.now()
log_array = []
modbus_client = ModbusTcpClient(Host.ip, Host.port)


@app.route("/")
def get_home():
    return ("<div><a href=\"time\">Last Action</a></div>"
            "<div><a href=\"log\">Show Log</a></div>"
            "<div><a href=\"info\">Show last state</a></div>"
            "<div><a href=\"debug\">Switch Debug Mode</a></div>")


@app.route("/time")
def get_time():
    return str(last_seen)


@app.route("/log")
def get_log():
    return (str(log_array)
            .replace(",", "</div><div>")
            .replace("[", "<div>")
            .replace("]", "</div>"))


@app.route("/info")
def get_info():
    return str(common_data_struct)


@app.route("/debug")
def get_debug():
    Common.debug = not Common.debug
    return str(Common.debug)


def check_modbus():
    global common_data_struct
    global modbus_client
    global last_seen
    try:
        modbus_client.connect()

        # get system mode
        readMode = modbus_client.read_holding_registers(Register.mode, 1, Device.vebus).registers[0]
        mode = Mode.name.get(readMode)

        debug("Mode : " + str(mode))
        common_data_struct["mode"] = mode

        # get state of charge
        readSoc = modbus_client.read_holding_registers(Register.soc, 1, Device.battery).registers[0]
        soc = readSoc / 10

        debug("SOC  : " + str(soc) + "%")
        common_data_struct["soc"] = str(soc)

        modeToSet = readMode

        if soc < 15:
            modeToSet = Mode.value.get("On")
        elif soc > 20:
            modeToSet = Mode.value.get("Inverter Only")

        if readMode != modeToSet:
            modeName = Mode.name.get(modeToSet)
            debug("set mode " + str(modeName))
            modbus_client.write_register(Register.mode, modeToSet, Device.vebus)

        last_seen = datetime.now()

    except Exception as e:
        error("An exception occurred: " + str(e))

    # Loop this function
    threading.Timer(Common.update_interval, check_modbus).start()


def debug(text):
    if Common.debug:
        print("DEBUG: " + text)
    add_to_log_array("DEBUG: " + text)


def error(text):
    print("ERROR: " + text)
    add_to_log_array("ERROR: " + text)


def log(text):
    print(text)
    add_to_log_array("LOG: " + text)


def add_to_log_array(text):
    global log_array
    log_array.insert(0, text)
    while len(log_array) > Common.log_capacity:
        log_array.pop()


if __name__ == "__main__":
    log("Starting App for: " + str(Host.ip) + ":" + str(Host.port))

    threading.Timer(1, check_modbus).start()

    app.run(host='0.0.0.0', port=8000, ssl_context='adhoc')
