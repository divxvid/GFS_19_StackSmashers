from socket import socket
import command_parser
import os
import threading

MESSAGE_SIZE = 1024 
MASTER_IP, MASTER_PORT = None, None
with open("master_ip.conf", "r") as f:
    MASTER_IP, MASTER_PORT = f.read().strip().split()
    MASTER_PORT = int(MASTER_PORT)


def send_chunks(ip, port, chunks, file_name):
    ssock = socket()
    ssock.connect((ip, port))
    for chunk in chunks:
        #TODO : logic for chunk sending.
        msg = f"Gimme chunks {chunk}"
        msg = msg + '\0'*(1024 - len(msg))
        ssock.send(str.encode(msg))
    ssock.close()

def upload_single_file(file_name):  
    if not os.path.isfile(file_name):
        print(f"{file_name} file not found.")
        return
    file_size = os.path.getsize(file_name)
    send_sock = socket()
    send_sock.connect((MASTER_IP, MASTER_PORT))
    str_to_send = "|".join(["U", file_name, str(file_size), ""])
    str_to_send = str_to_send + '\0'*(MESSAGE_SIZE - len(str_to_send))
    #encode the string into bytes
    str_bytes = str.encode(str_to_send)
    #print(f"Sending {len(str_bytes)} of data.")
    send_sock.send(str_bytes) 
    details = send_sock.recv(1024).decode()
    print("I got ", details)
    '''
    details format : E|1,5:127.0.0.1:3333|2:127.0.0.1:4444|3,4:127.0.0.1:5555|
    after parsing : [['1,5', '127.0.0.1', 3333], ['2', '127.0.0.1', 4444]]
    '''
    parsed_details = command_parser.command_parser(details)
    #print("Parsed details : ", parsed_details)
    for chunks, ip, port in parsed_details:
        chunk_nums = list(map(int, chunks.split(",")))
        print("chunk nums : ", chunk_nums)
        thread = threading.Thread(target=send_chunks, args=[ip, port, chunk_nums, file_name])
        thread.start()

    send_sock.close()

def upload_file(file_names): 
    for file_name in file_names:
        upload_single_file(file_name)        

while True:
    inp = input("> ")
    if inp == "":
        continue
    inp = inp.strip().split()
    command = inp[0]
    if command == "exit":
        break
    elif command == "upload":
        upload_file(inp[1:])
