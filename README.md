"# VictronModbusAutomation" 

Environment:  
MODBUS_HOST=CERBO_IP  
MODBUS_PORT=502  

Optional:  
UPDATE_INTERVAL=60  
LOG_CAPACITY=10000  
LOG_LEVEL="INFO"  

Docker:  
BUILD:  
docker build --tag victron-modbus-automation .

RUN:  
docker run --publish 8000:8000 -e MODBUS_HOST=CERBO_IP victron-modbus-automation

EXPORT IMAGE:  
docker save victron-modbus-automation -o dist/victron-modbus-automation.tar

IMPORT IMAGE:  
docker load -i dist/victron-modbus-automation.tar

Tag Image:
docker tag {{image_digest}} neongray/victron-modbus-automation:{{new_version}}
docker tag {{image_digest}} neongray/victron-modbus-automation:latest

Push Image:
docker push neongray/victron-modbus-automation:{{new_version}}
docker push neongray/victron-modbus-automation:latest
