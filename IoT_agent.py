import json
from bson import json_util
from kafka import KafkaConsumer
from kafka import KafkaProducer

import requests
import re
import io
import time

from threading import Thread

kafka_ip = "192.168.0.10" #'kafka1'
kafka_port = "9092"
kafka_url = kafka_ip + ':' + kafka_port

gcode_server_ip = "http://Gcode_server"
gcode_server_port = "9087"
gcode_server_url = gcode_server_ip + ':' + gcode_server_port

class Kafka_printers_status_retriever(Thread):
    def __init__ (self, printers_data, kafka_url):
        Thread.__init__(self)
        self.printers_data = printers_data
        self.producer = KafkaProducer(bootstrap_servers=kafka_url)

    def get_printer_status(self, printer):
        data = {
            "processStatus": "In Operation",
            "status": "Online"
        }

        recieved_info = self.get_info_from_api( self.printers_data[printer]['url'], 
                                                self.printers_data[printer]['api_token'], 
                                                'connection', 
                                                '"state":\s?"(.*?)"') #'"state":\s?"(.*?)"'
        if (recieved_info != -1):
            data['processStatus'] = recieved_info
            print ("processStatus: ", data['processStatus'])
        else:
            return -1

        recieved_info = self.get_info_from_api( self.printers_data[printer]['url'], 
                                                self.printers_data[printer]['api_token'], 
                                                'job', 
                                                '"state":\s?"(.*?)"') 
        if (recieved_info != -1):
            data['status'] = recieved_info
            print ("status: ",recieved_info)
        else:
            return -1

        return data

    # def get_json_info_from_api(self, url, api_key, resource):
    #     headers = {'Content-Type': 'application/json', 'X-Api-Key': api_key}
    #     try:
    #         response = requests.get(url + 'api/' + resource, headers=headers)
    #         response_json = json.load(response.text)
    #     except Exception as err:
    #         # TODO
    #         print (f'Error occurred while getting octoprint api info: {err}')
    #         if ('response' in locals()):
    #             print (response.text)
    #         return -1
    #     else:
    #         return response_json

    def get_info_from_api(self, url, api_key, resource, regex_search):
        headers = {'Content-Type': 'application/json', 'X-Api-Key': api_key}
        try:
            response = requests.get(url + 'api/' + resource, headers=headers)
            response_regex = re.findall(regex_search, response.text)[0]
        except Exception as err:
            # TODO
            print (f'Error occurred while getting octoprint api info: {err}')
            if ('response' in locals()):
                print (response.text)
            return -1
        else:
            return response_regex

    def run(self):
        while (True):
            data = {}
            for printer in self.printers_data:
                print ('Iterating printer data: ', printer)
                info = self.get_printer_status(printer)
                if info != -1:
                    data[printer] = info
            
            self.producer.send('printers_status', json.dumps(data, default=json_util.default).encode('utf-8'))
            time.sleep(1)

class Kafka_printers_controler(Thread):
    def __init__ (self, printers_data, kafka_url, gcode_server_url):
        Thread.__init__(self)
        self.printers_data = printers_data
        self.consumer = KafkaConsumer('orders',
                    group_id='my-group',
                    bootstrap_servers=kafka_url)
        self.gcode_server_url = gcode_server_url

    def upload_and_print(self, file_name, printer_url, api_key): 
        payload_file = {'file': open(file_name, 'rb')}
        url = printer_url + 'api/files/local'
        payload = {'select': 'true','print': 'true' }
        header = {'X-Api-Key': api_key }

        try:
            response = requests.post(url, files=payload_file, data=payload, headers=header, timeout=1)
        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error while updating file to the printer: {http_err}')
        except Exception as err:
            print(f'Error occurred while updating file to the printer: {err}')

    def get_gcode_and_record(self, printer, part):
        headers = {'Content-Type': 'application/json', 'printer':printer, 'part':part}
        url = self.gcode_server_url + '/get_gcode'

        try:
            response = requests.get(url, headers=headers, timeout=1)
        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error while geting gcode from server: {http_err}')
        except Exception as err:
            print(f'Error occurred while geting gcode from server: {err}')

        with open("file.gcode","wb") as f:
            f.write(response.text.encode("utf-8"))

    def decode_kafka_print_message(self, message):
        message_string = message.value.decode('utf8').replace("'", '"')
        
        # print (message_string)

        # Alternative method. Performance?
        # part = re.findall('"part": "(.*)", "pri', message_string )[0]

        message_json = json.loads(message_string)

        order_id = message_json['id']
        node = message_json['node']
        part = message_json['part']
        printer = message_json['printer']

        return (str(order_id), str(node), str(part), str(printer))

    def run(self):
        while (True):
            for message in self.consumer:
                (order_id, node, part, printer) = self.decode_kafka_print_message(message)
                print ('\n\nRecieved print order from kafka: ', order_id, node, part, printer)
                self.get_gcode_and_record(printer, part)

                if (printer in self.printers_data):
                    self.upload_and_print('file.gcode', printers[printer]['url'], printers[printer]['api_token'])
                else:
                    # TODO a best alternative here?
                    print ("This printer is not listed")

def main():
    printers = {}
    with open('printers_conf.txt') as printers_file:
    # with open('/home/configuration/printers_conf.txt') as printers_file:
        printers = json.load(printers_file)

    for printer in printers:
        try:
            test = printers[printer]['url']
            test = printers[printer]['api_token']
        except Exception as err:
            print(f'Error reading printer configurations file: {printer}:{err}')
            exit()

    monitor_thread = Kafka_printers_status_retriever(printers, kafka_url)
    monitor_thread.start()

    control_thread = Kafka_printers_controler(printers, kafka_url, gcode_server_url)
    control_thread.start()

if __name__ == '__main__':
    main()
