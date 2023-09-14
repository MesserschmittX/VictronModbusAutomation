from pymodbus.client import ModbusTcpClient
from flask import Flask

import threading
import atexit

from values import Mode, Device, Register, Host

app = Flask(__name__)


@app.route('/')
def get_json():
    return common_data_struct


POOL_TIME = 10  # Seconds

# variables that are accessible from anywhere
common_data_struct = {}
modbus_client = ModbusTcpClient(Host.ip, Host.port)
# lock to control access to variable
data_lock = threading.Lock()
# timer handler
modbus_timer = threading.Timer(0, lambda x: None, ())


def create_app():
    def interrupt():
        global modbus_timer
        modbus_timer.cancel()

    def check_modbus():
        global common_data_struct
        global modbus_timer
        global modbus_client
        with data_lock:
            try:
                modbus_client.connect()

                # get system mode
                readMode = modbus_client.read_holding_registers(Register.mode, 1, Device.vebus).registers[0]
                mode = Mode.name.get(readMode)

                print("Mode is: " + mode)
                common_data_struct["mode"] = "Mode is: " + mode

                # get state of charge
                readSoc = modbus_client.read_holding_registers(Register.soc, 1, Device.battery).registers[0]
                soc = readSoc / 10

                print("SOC is: " + str(soc) + "%")
                common_data_struct["soc"] = "SOC is: " + str(soc) + "%"

                modeToSet = 0

                if soc < 15:
                    modeToSet = Mode.value.get("On")
                elif soc > 20:
                    modeToSet = Mode.value.get("Inverter Only")

                if readMode != modeToSet:
                    print("set mode " + Mode.name.get(modeToSet))
                    modbus_client.write_register(Register.mode, modeToSet, Device.vebus)
            except Exception as error:
                print("An exception occurred:", error)


        # Set the next timeout to happen
        modbus_timer = threading.Timer(POOL_TIME, check_modbus, ())
        modbus_timer.start()

    def do_stuff_start():
        # Do initialisation stuff here
        global modbus_timer
        global modbus_client
        # Create your timer
        modbus_timer = threading.Timer(POOL_TIME, check_modbus, ())
        modbus_timer.start()

    # Initiate
    do_stuff_start()
    # When you kill Flask (SIGTERM), cancels the timer
    atexit.register(interrupt)
    return app


app = create_app()


'''

while True:
    try:
        modbus_client.connect()

        # get system mode
        readMode = modbus_client.read_holding_registers(modeAddress, 1, vebusID).registers[0]
        mode = ReverseMode.get(readMode)

        print("Mode is: " + mode)
        displayData["mode"] = "Mode is: " + mode

        # get state of charge
        readSoc = modbus_client.read_holding_registers(socAddress, 1, batteryID).registers[0]
        soc = readSoc / 10

        print("SOC is: " + str(soc) + "%")
        displayData["soc"] = "SOC is: " + str(soc) + "%"

        modeToSet = 0

        if soc < 15:
            modeToSet = Mode.get("On")
        elif soc > 20:
            modeToSet = Mode.get("Inverter Only")

        if readMode != modeToSet:
            print("set mode " + ReverseMode.get(modeToSet))
            modbus_client.write_register(modeAddress, modeToSet, vebusID)
    except Exception as error:
        print("An exception occurred:", error)

    time.sleep(5)
'''
