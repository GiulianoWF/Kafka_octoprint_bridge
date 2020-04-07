import json
from bson import json_util
from kafka import KafkaConsumer
from kafka import KafkaProducer

import requests
import re
import io

def upload_and_print(file_name, printer_url, api_key): 
    payload_file = {'file': open(file_name, 'rb')}
    url = printer_url + 'api/files/local'
    print (url)
    payload = {'select': 'true','print': 'true' }
    header = {'X-Api-Key': api_key }
    response = requests.post(url, files=payload_file, data=payload, headers=header)
    print(response.text)

def main(args=None):
    kafka_ip = "127.0.0.1"
    kafka_port = "9092"


    gcode_server_ip = "http://127.0.0.1"
    gcode_server_port = "9087"

    printers = [{"name":"printer1", "url":"http://127.0.0.1:5001/", "api_token":'92EB3B3F646A4BC4B8EBD7868A265F9E'}]
    
    # Producer will be used to send status
    # producer = KafkaProducer(bootstrap_servers=kafka_ip+':'+kafka_port)
    consumer = KafkaConsumer('orders',
                         group_id='my-group',
                         bootstrap_servers=kafka_ip+':'+kafka_port)

    while (True):
        #Thread1==========================================
        for message in consumer:
            message_string = message.value.decode('utf8').replace("'", '"')
            
            # Alternative method. Performance?
            print (message_string)
            # part = re.findall('"part": "(.*)", "pri', message_string )[0]

            message_json = json.loads(message_string)

            order_id = message_json['id']
            node = message_json['node']
            part = message_json['part']
            printer = message_json['printer']

            print (order_id, node, part, printer)

            headers = {'Content-Type': 'application/json', 'printer':str(printer), 'part':str(part)} #, 'X-Api-Key': api_key}
            url = gcode_server_ip + ':' + gcode_server_port + '/get_gcode'
            response = requests.get(url, headers=headers)
            print (response.text)

            # if (response.text is 'No such file or directory'):
            #      continue

            # TODO super slow
            with open("file.gcode","wb") as f:
                f.write(response.text.encode("utf-8"))
            # pseudo_file = io.StringIO(response.text)

            #TODO printer number from array
            printer_number = 0
            upload_and_print('file.gcode', printers[printer_number]['url'], printers[printer_number]['api_token'])

            while (True):
                pass

if __name__ == '__main__':
    main()
