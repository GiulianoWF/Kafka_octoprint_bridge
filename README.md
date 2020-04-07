# Kafka_octoprint_bridge
Uses kafka to control 3d printers

run the command
docker-compose up
to start kafka broker + zookeper + one instance of octoprint

build ./Gcode_server/Gcode_server.cpp with the command 
g++ -Iincludes -Llibs Gcode_server.cpp -lpistache -lpthread

After that access the octoprint address and go thought the wizard.
(It is possible that octoprint require  internet access at least one time, after the wizard is run, in order to start working.)

Then run the Gcode_server + IoT_agent.py + emissor_ordens.py and see the printer move.
