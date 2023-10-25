"# VictronModbusAutomation" 

Environment:  
MODBUS_HOST=CERBO_IP  
MODBUS_PORT=502  

Optional:  
UPDATE_INTERVAL=60  
LOG_CAPACITY=10000  
DEBUG=False  

Docker:  
BUILD:  
docker build --tag victron-modbus-automation .

RUN:  
docker run --publish 8000:8000 -e MODBUS_HOST=CERBO_IP victron-modbus-automation

EXPORT IMAGE:  
docker save victron-modbus-automation -o dist/victron-modbus-automation.tar

IMPORT IMAGE:  
docker load -i dist/victron-modbus-automation.tar
