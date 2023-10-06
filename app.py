from datetime import datetime
from pymodbus.client import ModbusTcpClient
import threading

from values import Mode, Device, Register, Host, Common

# variables that are accessible from anywhere
common_data_struct = {}
last_seen = datetime.now()
log_array = []
modbus_client = ModbusTcpClient(Host.ip, Host.port)


def check_modbus():
    global common_data_struct
    global modbus_client
    global last_seen
    try:
        modbus_client.connect()

        # get system mode
        readMode = modbus_client.read_holding_registers(Register.mode, 1, Device.vebus).registers[0]
        mode = Mode.name.get(readMode)

        debug("Mode : " + mode)
        common_data_struct["mode"] = mode

        # get state of charge
        readSoc = modbus_client.read_holding_registers(Register.soc, 1, Device.battery).registers[0]
        soc = readSoc / 10

        debug("SOC  : " + str(soc) + "%")
        common_data_struct["soc"] = str(soc)

        modeToSet = 0

        if soc < 15:
            modeToSet = Mode.value.get("On")
        elif soc > 20:
            modeToSet = Mode.value.get("Inverter Only")

        if readMode != modeToSet:
            debug("set mode " + Mode.name.get(modeToSet))
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
    while len(log_array) > 1000:
        log_array.pop()


def print_cli_commands():
    print("###############################\n"
          "time:\tlast update\n"
          "log:\tlog array\n"
          "info:\tlast data from modbus\n"
          "quit:\tstop execution\n"
          "debug:\ttoggle debug mode\n"
          "###############################")


def cli_handler():
    run = True
    while run:
        command = input()
        match command:
            case "quit" | "q":
                run = False
            case "time" | "t":
                print(last_seen)
            case "log" | "l":
                print(log_array)
            case "info" | "i":
                print(common_data_struct)
            case "debug" | "d":
                Common.debug = not Common.debug
                print("Debu mode: " + str(Common.debug))
            case other:
                print_cli_commands()


if __name__ == "__main__":
    log("Starting App for: " + str(Host.ip) + ":" + str(Host.port))

    debug("Debug mode is enabled")

    threading.Timer(1, check_modbus).start()

    print_cli_commands()
    # TODO use threading approach when REST Framework needs the main Thread
    # threading.Thread(target=cli_handler).start()
    cli_handler()
