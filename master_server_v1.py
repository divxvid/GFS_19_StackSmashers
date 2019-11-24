#!/usr/bin/python3

import os
from socket import socket
import threading
import math
import json
import time

CHUNK_SIZE = 524288
MESSAGE_SIZE = 1024
chunk_id=1
dict_chunk_details={}
dict_all_chunk_info={}
dict_size_info={}
dict_status_bit={}
dict_chunkserver_ids={}

def checkStatus(temp_list) :
    print(temp_list[0], temp_list[1])
    chunk_ip = str(temp_list[0])
    chunk_port = int(temp_list[1])
    chunk_sock = socket()
    chunk_sock.settimeout(1)
    flag = 0
    try :
        chunk_sock.connect((chunk_ip, chunk_port))
    except ConnectionRefusedError :
        flag = 1
    if flag == 0 :
        str3 = "H|"
        message1 = str3 + '\0'*(MESSAGE_SIZE - len(str3))
        chunk_sock.send(message1.encode())
        try :
            message = chunk_sock.recv(1024).decode()
            if message[0] != 'A' :
                flag = 1
        except socket.timeout: # fail after 1 second of no activity
            flag = 1
    temp_str = temp_list[0] + ":" + temp_list[1]
    if flag == 1 :
        if dict_status_bit[temp_str] == 'A' :
            dict_status_bit[temp_str] = 'C'
        elif dict_status_bit[temp_str] == 'C' :
            dict_status_bit[temp_str] = 'D'
    elif flag == 0 :
        dict_status_bit[temp_str] = 'A'
    chunk_sock.close()

def checkChunkServers() :
    list_ip_port_input = []
    with open("chunk_server_info.conf", "r") as fp1:
        for line in fp1.readlines():
            list_ip_port_input.append(line.strip().split())
    while True :
        for chunk_server_details in list_ip_port_input :
            checkStatus(chunk_server_details)
        print(dict_status_bit)
        time.sleep(10)

def connect_when_replica(ip_port,str_to_send):
    temp_list=ip_port.split(":")
    chunk_ip = str(temp_list[0])
    chunk_port = int(temp_list[1])
    chunk_sock = socket()
    chunk_sock.connect((chunk_ip, chunk_port))
    message1 =str_to_send + '\0'*(MESSAGE_SIZE - len(str_to_send))
    print(message1)
    chunk_sock.send(message1.encode())

def send_replica_info_all(file_name,dict_chunk_details):
    dict_chunkid_ipport={}
    for key,value in dict_chunk_details[file_name]['P'].items():
        for i in value:
            dict_chunkid_ipport[i]=key
    for key,value in dict_chunk_details[file_name]['S'].items():
        str_to_send="R|"
        str_temp=""
        temp=""
        #print(value)
        str_temp=','.join(value)
        str_to_send=str_to_send+str_temp+":"+dict_chunkid_ipport[value[0]]+"|"
        #print(key)
        #print(str_to_send)
        connect_when_replica(key,str_to_send)

def formattojson(file_size,file_name,final_list_chunks,list_ip_port):
    temp_dict_pri={}
    list_temp=[]
    for list1 in final_list_chunks:
        for j in list1:
            list_temp.append(j)
    dict_all_chunk_info[file_name]=list_temp
    dict_size_info[file_name]=file_size
    i=0
    for list1 in final_list_chunks:
        temp=list_ip_port[i][0]+":"+list_ip_port[i][1]
        temp_dict_pri[temp]=list1
        i=i+1
    i=1
    temp_dict_sec={}
    for list1 in final_list_chunks:
        temp=list_ip_port[i][0]+":"+list_ip_port[i][1]
        temp_dict_sec[temp]=list1
        i=(i+1)%len(list_ip_port)

    temp_dict={}
    temp_dict['P']=temp_dict_pri
    temp_dict['S']=temp_dict_sec
    dict_chunk_details[file_name]=temp_dict
    with open('file_table.json', 'w') as outfile:
        json.dump(dict_chunk_details, outfile)
    with open('file_chunk_info.json', 'w') as outfile:
        json.dump(dict_all_chunk_info, outfile)
    with open('file_size.json', 'w') as outfile:
        json.dump(dict_size_info, outfile)
    send_replica_info_all(file_name,dict_chunk_details)

    #print(dict_chunk_details)
def create_status():
    list_ip_port = []
    with open("chunk_server_info.conf", "r") as fp1:
        for line in fp1.readlines():
            list_ip_port.append(line.strip().split())
    for list1 in list_ip_port :
        temp=list1[0]+":"+list1[1]
        dict_status_bit[temp]="D"

def create_dict_chunkserver(list_ip_port,final_list_chunks):
    i=0
    for list1 in list_ip_port:
        list3=[]
        temp=list1[0]+":"+list1[1]
        if temp in dict_chunkserver_ids:
            for ids in dict_chunkserver_ids[temp]:
                list3.append(ids)
        for j in final_list_chunks[i]:
            list3.append(j)
        dict_chunkserver_ids[temp]=list3
        i=i+1
    print(dict_chunkserver_ids)
#read from meta data of master and prepare the string to be sent to client

def uploadChunks(data_from_client) :
    print(f"upload {data_from_client[1]} {data_from_client[2]}")
    global chunk_id
    list_ip_port_input=[]
    list_ip_port = []
    with open("chunk_server_info.conf", "r") as fp1:
        for line in fp1.readlines():
            list_ip_port_input.append(line.strip().split())

    for list1 in list_ip_port_input :
        temp_str = list1[0]+":"+list1[1]
        if dict_status_bit[temp_str] == 'A' :
            list_ip_port.append(list1)

    file_name=data_from_client[1]
    file_size = int(data_from_client[2])
    no_of_chunk_servers = len(list_ip_port)
    no_of_chunks = math.ceil(file_size/CHUNK_SIZE)
    print("no of chunks ", no_of_chunks)
    data_info={}

    final_list_chunks = list()
    for i in range(1,no_of_chunk_servers+1) :
        temp_list1 = list()
        counter = 0
        while i+(counter*no_of_chunk_servers) <= no_of_chunks :
            temp_list1.append(str(i+chunk_id+(counter*no_of_chunk_servers)))
            counter = counter + 1
        final_list_chunks.append(temp_list1)
    chunk_id+=no_of_chunks
    #print(final_list_chunks)
    formattojson(file_size,file_name,final_list_chunks,list_ip_port)
    create_dict_chunkserver(list_ip_port,final_list_chunks)
    str3 = 'E'
    str_to_send = ""
    for i in range(0, len(final_list_chunks)) :
        if i == no_of_chunks:
            break
        str1 = ','.join(final_list_chunks[i])
        str2 = ':'.join([str1, list_ip_port[i][0], list_ip_port[i][1]])
        str3 = '|'.join([str3, str2])
    str3 = f"{str3}|"
    str_to_send = str3 + '\0'*(MESSAGE_SIZE - len(str3))
    #print("String to send ", str_to_send)
    return str_to_send

def downloadChunks(data_from_client) :
    print(f"download {data_from_client[1]} {data_from_client[2]}")

#accept request from client and call function accordingly and send reply to client
def accceptRequest(data_from_client, send_sock) :
    if data_from_client[0] == 'U' :
        str_bytes = ""
        temp_str = ""
        temp_str = uploadChunks(data_from_client)
        str_bytes = str.encode(temp_str)
        send_sock.send(str_bytes)
        send_sock.close()
    elif data_from_client[0] == 'D' :
        downloadChunks(data_from_client)

def clientReceive() :
    fp1 = open("master_ip.conf", "r")
    read_data = fp1.readline().strip()
    fp1.close()
    master_ip, master_port = read_data.split(" ")
    print(f"{master_ip} {master_port}")
    master_sock = socket()
    master_sock.bind(("", int(master_port)))
    master_sock.listen(10)
    while True :
        client_sock, client_addr = master_sock.accept()
        packet = client_sock.recv(1024)
        packet_from_client = packet.decode()
        data_from_client = packet_from_client.split("|")
        thread1 = threading.Thread(target = accceptRequest, args = (data_from_client, client_sock, ))
        thread1.start()
        #thread1.join()
    master_sock.close()


if __name__ == "__main__" :
    create_status()
    thread1 = threading.Thread(target = checkChunkServers)
    thread1.start()
    clientReceive() 
    