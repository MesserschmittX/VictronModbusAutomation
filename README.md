"# VictronModbusAutomation" 

Environment
MODBUS_HOST=CERBO_IP
MODBUS_PORT=502

Docker
BUILD: docker build --tag victron-modbus-automation .
RUN: docker run --publish 8000:8000 victron-modbus-automation
EXPORT IMAGE: docker save victron-modbus-automation > dist/victron-modbus-automation.tar

Debug
RUN: python -m flask run