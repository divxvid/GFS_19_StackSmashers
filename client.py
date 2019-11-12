from socket import socket, AF_INET, SOCK_STREAM
import command_parser
import os
import threading

MESSAGE_SIZE = 1024
CHUNK_SIZE= 512 * 1024 #512K
MASTER_IP, MASTER_PORT = None, None
with open("master_ip.conf", "r") as f:
    MASTER_IP, MASTER_PORT = f.read().strip().split()
    MASTER_PORT = int(MASTER_PORT)

def i_to_s(x):
    msg = f"N|{x}|"
    msg = msg + '\0' * (MESSAGE_SIZE - len(msg))
    return msg

def send_single_chunk(f, sock, chunk_number):
    #sleep(20)
    msg = i_to_s(chunk_number)
    print("Send Chunk number : ", msg)
    msg = str.encode(msg)
    sock.send(msg)
    f.seek((chunk_number-1)*CHUNK_SIZE)
    c_data = f.read(CHUNK_SIZE)
    read_size = len(c_data)
    msg = i_to_s(read_size)
    msg = str.encode(msg)
    sock.send(msg)
    ctr = 0
    while read_size > 0 :
        dts = c_data[ctr:ctr+MESSAGE_SIZE]
        sock.send(dts)
        read_size -= len(dts)
        ctr += len(dts)

    print(f"{chunk_number} sent")


def send_chunks(ip, port, chunks, file_name):
    ssock = socket(AF_INET, SOCK_STREAM)
    ssock.connect((ip, port))
    f_name = f"T|{file_name}|"
    f_name = f_name + '\0'*(MESSAGE_SIZE - len(f_name))
    ssock.send(str.encode(f_name))
    num_chunks = i_to_s(len(chunks))
    ssock.send(str.encode(num_chunks))
    f = open(file_name, "rb")
    for chunk in chunks:
        send_single_chunk(f, ssock, chunk)
    f.close()
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
    print(f"Sending {len(str_bytes)} of data.")
    send_sock.send(str_bytes)
    details = send_sock.recv(MESSAGE_SIZE).decode()
    print("I got ", details)
    '''
    details format : E|1,5:127.0.0.1:3333|2:127.0.0.1:4444|3,4:127.0.0.1:5555|
    after parsing : [['1,5', '127.0.0.1', 3333], ['2', '127.0.0.1', 4444]]
    '''
    parsed_details = command_parser.command_parser(details)
    print("Parsed details : ", parsed_details)
    thread_list = list()
    for chunks, ip, port in parsed_details:
        chunk_nums = list(map(int, chunks.split(",")))
        print("chunk nums : ", chunk_nums)
        thread = threading.Thread(target=send_chunks, args=[ip, port, chunk_nums, file_name])
        thread.start()
        thread_list.append(thread)

    for thread in thread_list:
        thread.join()

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
