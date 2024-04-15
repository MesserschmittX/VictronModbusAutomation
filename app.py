import time
import threading
from datetime import datetime
from pymodbus.client import ModbusTcpClient
from flask import Flask, render_template, request

from values import Mode, Device, Register, Host, Common, Battery

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

# variables that are accessible from anywhere
common_data_struct = {}
last_seen = datetime.now()
log_array = []
modbus_client = ModbusTcpClient(Host.ip, Host.port)


class LogLevel:
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    ERROR = 'ERROR'


@app.route("/")
def get_home():
    return ("<div><a href=\"time\">Last Action</a></div>"
            "<div><a href=\"log\">Show Log</a></div>"
            "<div><a href=\"info\">Show last state</a></div>"
            "<div><a href=\"settings\">Settings Page</a></div>")


@app.route("/time")
def get_time():
    return str(last_seen)


@app.route("/log")
def get_log():
    return (str(log_array)
            .replace(",", "</div><div>")
            .replace("'", "")
            .replace("[", "<div>")
            .replace("]", "</div>")
            .replace("DEBUG: ", '<span style="color:blue">DEBUG: </span>')
            .replace("ERROR: ", '<span style="color:red">ERROR: </span>'))


@app.route("/info")
def get_info():
    return str(common_data_struct)


@app.route('/settings')
def get_settings():
    return render_template('settings.html', Battery=Battery, Common=Common)


@app.route('/submit', methods=['POST'])
def submit():
    errors = []

    # get grid connect settings
    high_connect_to_grid_above = int(request.form['high_connect_to_grid_above'])
    high_disconnect_from_grid_below = int(request.form['high_disconnect_from_grid_below'])
    low_connect_to_grid_below = int(request.form['low_connect_to_grid_below'])
    low_disconnect_from_grid_above = int(request.form['low_disconnect_from_grid_above'])

    # get log level
    Common.log_level = request.form['log_level']

    if high_connect_to_grid_above < high_disconnect_from_grid_below:
        errors.append("Battery high disconnect needs to be above reconnect")
    if low_disconnect_from_grid_above < low_connect_to_grid_below:
        errors.append("Battery low disconnect needs to be below reconnect")
    if (low_disconnect_from_grid_above > high_connect_to_grid_above
            or low_connect_to_grid_below > high_disconnect_from_grid_below):
        errors.append("Battery low values need to be below battery high values")

    if len(errors) == 0:
        Battery.high_connect_to_grid_above = high_connect_to_grid_above
        Battery.high_disconnect_from_grid_below = high_disconnect_from_grid_below
        Battery.low_connect_to_grid_below = low_connect_to_grid_below
        Battery.low_disconnect_from_grid_above = low_disconnect_from_grid_above
        return "Form submitted successfully"
    else:
        return "Error:" + "\n\t".join(errors)


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

        if soc < Battery.low_connect_to_grid_below or soc > Battery.high_connect_to_grid_above:
            modeToSet = Mode.value.get("On")
        elif Battery.low_disconnect_from_grid_above < soc < Battery.high_disconnect_from_grid_below:
            modeToSet = Mode.value.get("Inverter Only")

        if readMode != modeToSet:
            modeName = Mode.name.get(modeToSet)
            info("set mode " + str(modeName))
            modbus_client.write_register(Register.mode, modeToSet, Device.vebus)

        last_seen = datetime.now()

    except Exception as e:
        error("An exception occurred: " + str(e))

    # Loop this function
    threading.Timer(Common.update_interval, check_modbus).start()


def debug(text):
    timestamp = str(datetime.now())
    if Common.log_level == LogLevel.DEBUG:
        print(timestamp + ": " + "DEBUG: " + text)
        add_to_log_array("DEBUG: " + text)


def info(text):
    timestamp = str(datetime.now())
    if Common.log_level == LogLevel.DEBUG or Common.log_level == LogLevel.INFO:
        print(timestamp + ": " + "INFO: " + text)
        add_to_log_array("INFO: " + text)


def error(text):
    timestamp = str(datetime.now())
    print(timestamp + ": " + "ERROR: " + text)
    add_to_log_array("ERROR: " + text)


def log(text):
    timestamp = str(datetime.now())
    print(timestamp + ": " + text)
    add_to_log_array("LOG: " + text)


def add_to_log_array(text):
    global log_array
    timestamp = str(datetime.now())
    log_array.insert(0, timestamp + ": " + text)
    while len(log_array) > Common.log_capacity:
        log_array.pop()


if __name__ == "__main__":
    log("Starting App for: " + str(Host.ip) + ":" + str(Host.port))

    threading.Timer(1, check_modbus).start()

    app.run(host='0.0.0.0', port=8000, ssl_context='adhoc')
