"# VictronModbusAutomation" 

Docker
BUILD: docker build --tag victron-modbus-automation .
RUN: docker run --publish 5000:5000 victron-modbus-automation

Debug
RUN: python -m flask run