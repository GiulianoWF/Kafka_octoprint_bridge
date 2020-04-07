import json
from bson import json_util
from kafka import KafkaProducer

import time

import requests
import re

def main(args=None):
    kafka_ip = "127.0.0.1"
    kafka_port = "9092"

    producer = KafkaProducer(bootstrap_servers=kafka_ip+':'+kafka_port)

    data = {
            "id": 123456789,
            "node": "PUCRS_LabCIM_1",
            "part": "mask",
            "printer": "printer1"
    }

    while (True):
        producer.send('orders', json.dumps(data, default=json_util.default).encode('utf-8'))
        time.sleep(2)



if __name__ == '__main__':
    main()
