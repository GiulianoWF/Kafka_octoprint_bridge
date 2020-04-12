import json
from bson import json_util
from kafka import KafkaConsumer
from kafka import KafkaProducer


kafka_ip = "127.0.0.1"
kafka_port = "9092"

consumer = KafkaConsumer('printers_status',
                         group_id='my-group',
                         bootstrap_servers=kafka_ip+':'+kafka_port)
while (True):
    for message in consumer:
        message_string = message.value.decode('utf8').replace("'", '"')
        
        print (message_string)
