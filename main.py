from pymodbus.client import ModbusTcpClient
import time

host = '10.10.11.118'
port = 502
vebusID = 227
batteryID = 225
modeAddress = 33
socAddress = 266

Mode = {
    "Charger Only": 1,
    "Inverter Only": 2,
    "On": 3,
    "Off": 4
}
ReverseMode = {
    1: "Charger Only",
    2: "Inverter Only",
    3: "On",
    4: "Off"
}

client = ModbusTcpClient(host, port)
while True:
    try:
        client.connect()

        # get system mode
        readMode = client.read_holding_registers(modeAddress, 1, vebusID).registers[0]
        mode = ReverseMode.get(readMode)

        print("Mode is: " + mode)

        # get state of charge
        readSoc = client.read_holding_registers(socAddress, 1, batteryID).registers[0]
        soc = readSoc / 10

        print("SOC is: " + str(soc) + "%")

        modeToSet = 0

        if soc < 15:
            modeToSet = Mode.get("On")
        elif soc > 20:
            modeToSet = Mode.get("Inverter Only")

        if readMode != modeToSet:
            print("set mode " + ReverseMode.get(modeToSet))
            client.write_register(modeAddress, modeToSet, vebusID)
    except Exception as error:
        print("An exception occurred:", error)

    time.sleep(60)
