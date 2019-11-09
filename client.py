from socket import socket
import os

MESSAGE_SIZE = 1024 
MASTER_IP, MASTER_PORT = None, None
with open("master_ip.conf", "r") as f:
    MASTER_IP, MASTER_PORT = f.read().strip().split()
    MASTER_PORT = int(MASTER_PORT)

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
    print(str_bytes)
    print(f"Sending {len(str_bytes)} of data.")
    send_sock.send(str_bytes) 
    details = send_sock.recv(1024)
    print("I got ", details.decode())
    send_sock.close()

def upload_file(file_names): 
    for file_name in file_names:
        upload_single_file(file_name)        

while True:
    inp = input("> ").strip().split()
    command = inp[0]
    if command == "exit":
        break
    elif command == "upload":
        upload_file(inp[1:])
