#!/usr/bin/python3

import os
from socket import socket
import threading
import math

CHUNK_SIZE = 524288
MESSAGE_SIZE = 1024

#read from meta data of master and send the string to client
def uploadChunks(data_from_client) :
    print(f"upload {data_from_client[1]} {data_from_client[2]}")
    list_ip_port = []
    list1 = ['127.0.0.1','50001']
    list2 = ['127.0.0.2','50002']
    list3 = ['127.0.0.3','50003']
    list4 = ['127.0.0.4','50004']
    list_ip_port.append(list1)
    list_ip_port.append(list2)
    list_ip_port.append(list3)
    list_ip_port.append(list4)
    file_size = int(data_from_client[2])
    no_of_chunk_servers = 4
    no_of_chunks = math.ceil(file_size/CHUNK_SIZE)
    final_list_chunks = list()
    for i in range(1,no_of_chunk_servers+1) :
        temp_list1 = list()
        counter = 0
        while i+(counter*no_of_chunk_servers) <= no_of_chunks :
            temp_list1.append(str(i+(counter*no_of_chunk_servers)))
            counter = counter + 1
        final_list_chunks.append(temp_list1)
    print(final_list_chunks)
    str3 = 'E'
    str_to_send = ""
    for i in range(0,no_of_chunk_servers) :
        str1 = ','.join(final_list_chunks[i])
        str2 = ':'.join([str1, list_ip_port[i][0], list_ip_port[i][1]])
        str3 = '|'.join([str3, str2])
    str3 = f"{str3}|"
    str_to_send = str3 + '\0'*(MESSAGE_SIZE - len(str3))
    print(len(str_to_send))
    str_bytes = str.encode(str_to_send)

def downloadChunks(data_from_client) :
    print(f"download {data_from_client[1]} {data_from_client[2]}")

#accept request from client and call function accordingly
def accceptRequest(data_from_client) :
    if data_from_client[0] == 'U' :
        uploadChunks(data_from_client)
    elif data_from_client[0] == 'D' :
        downloadChunks(data_from_client)

def clientReceive() :
    fp1 = open("master_ip.conf", "r")
    read_data = fp1.readline()
    master_ip, master_port = read_data.split(" ")
    print(f"{master_ip} {master_port}")
    master_sock = socket()
    master_sock.bind(("", int(master_port)))
    master_sock.listen(10)
    while True :
        # client_sock, client_addr = master_sock.accept()
        # packet = client_sock.recv(1024)
        # packet_from_client = packet.decode()
        # print(packet_from_client)
        packet_from_client=input()
        data_from_client = packet_from_client.split("|")
        # print(data_from_client)
        thread1 = threading.Thread(target = accceptRequest, args = (data_from_client,))
        thread1.start()
        thread1.join()
        # client_sock.close()
    master_sock.close()


if __name__ == "__main__":
    clientReceive()
