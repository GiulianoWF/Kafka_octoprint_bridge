# Kafka_octoprint_bridge
Uses kafka to control 3d printers

run the command
docker-compose up
to start kafka broker + zookeper + one instance of octoprint

build ./Gcode_server/Gcode_server.cpp with the command 
g++ -Iincludes -Llibs Gcode_server.cpp -lpistache -lpthread

Then run the Gcode_server + IoT_agent.py + emissor_ordens.py and see the printer move.
