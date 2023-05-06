#!/usr/bin/env python3

import socket
from alarmeitbl.utils_tx import *
from time import time
from time import sleep
from watchdog.observers import Observer
from tx import utils_file

HOST = "localhost"  # The server's hostname or IP address
PORT = 9009  # The port used by the server

KEEPALIVE_INTERVAL = 60
next_heartbeat = 0    
ack_response = b'\x00'
panel_is_connected = False
success_ack_time = time()

client_data = {
    'account': '0001',
    'mac': '400021',
    'command': '94',
    'channel': '45',
    'event':'130',
    'identifier': '18',
    'qualifier': '1',
    'partition': '00',
    'zone':'001'
    }

#teste

util = UtilsTX()

data_list = util.create_array(client_data)
data_list.insert(0, str(hex(len(data_list))).zfill(2)) #add packet size
data_list_int = [int(x, 16) for x in data_list]
data_list_int.extend([util.checksum(data_list)]) #add checksum

if __name__ == "__main__":   
    file_path = 'event_buffer.txt'
    event_handler = utils_file.FileHandler()
    observer = Observer()
    observer.schedule(event_handler, file_path, recursive=True)
    observer.start()    

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    sock.connect((HOST, PORT))

    sock.sendall(bytes(data_list_int))     
    print('Sent: ', data_list)              
    ack_response = sock.recv(1024) 

    if ack_response == b'\xfe':
        print('Received:', ack_response)    
        print('Connection estabilished')
        success_ack_time = time()
        next_heartbeat = success_ack_time + KEEPALIVE_INTERVAL  
        panel_is_connected = True

    while True:          
        try:
            if panel_is_connected and event_handler.new_event and event_handler.is_valid:                             
                client_data.update(event_handler.alarm_event)
                
                data_list = util.create_array(client_data)
                data_list.insert(0, str(hex(len(data_list))).zfill(2)) #add packet size
                data_list_int = [int(x, 16) for x in data_list]
                data_list_int.extend([util.checksum(data_list)]) #add checksum
                
                print('Event sent:', bytes(data_list_int))   
                sock.sendall(bytes(data_list_int))               
                ack_response = sock.recv(1024) 
                print('Received:', ack_response)

                if ack_response == b'\xfe':                 
                    success_ack_time = time()
                    next_heartbeat = success_ack_time + KEEPALIVE_INTERVAL                                      
                    
            if panel_is_connected and time() > next_heartbeat and not event_handler.new_event:            
                sock.send(b'\xF7')
                print('Heartbeat Sent:', b'\xF7')  
                ack_response = sock.recv(1024) 
                print('Received:', ack_response)             
                success_ack_time = time()
                next_heartbeat = success_ack_time + KEEPALIVE_INTERVAL            
        
        except socket.error:                  
            observer.stop()
            raise Exception("Socket error! Check Server and try again.")    
        
