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

def s_to_i(msg):
    parts = msg.split("|")
    if parts[0] == "N":
        return int(parts[1])
    return None

def i_to_s(x):
    msg = f"N|{x}|"
    msg = msg + '\0' * (MESSAGE_SIZE - len(msg))
    return msg

def merge(file_name,chunk_num):
    chunk_num = list(map(int, chunk_num))
    chunk_num.sort()
    chunk_files = [str(x)+".chunk" for x in chunk_num]
    with open(file_name, 'wb') as outfile:
        for fname in chunk_files:
            print('copying',fname)
            with open(fname,"rb") as infile:
                outfile.write(infile.read())
            if os.path.exists(fname):
                os.remove(fname)

def connect_to_chunk_Server(details):	#	['1,5', '127.0.0.1', 3333]
    csock = socket(AF_INET, SOCK_STREAM)
    csock.connect((details[1], details[2]))
    command = "X|{}|".format(details[0])
    command = command + '\0'*(MESSAGE_SIZE - len(command))
    cmd_bytes = str.encode(command)
    print(f"Sending {len(cmd_bytes)} of data.")
    csock.send(cmd_bytes)
    c_no = details[0].split(",")
    for c in c_no:
    	with open(f"{c}.chunk", "wb") as f :
            read_size = csock.recv(MESSAGE_SIZE).decode()
            read_size = s_to_i(read_size)
            while read_size > 0:
                dr = csock.recv(MESSAGE_SIZE)
                f.write(dr)
                read_size -= len(dr)
            csock.send(str.encode("A"*1024))
        	# recv_file(csock,chunk_ids)

def chunk_server_details(parsed_details,file_name):
    all_chunk_ids = []
    thread_list = list()
    for i in parsed_details :
        if i[0] == '':
            continue
        chunk_list = i[0].split(',')
        for j in chunk_list :
            all_chunk_ids.append(j)
        # connect_to_chunk_Server(i)
        thread = threading.Thread(target=connect_to_chunk_Server, args=[i])
        thread.start()
        thread_list.append(thread)

    for thread in thread_list:
        thread.join()
    merge(file_name,all_chunk_ids)

def send_single_chunk(f, sock, chunk_number, offset):
    #sleep(20)
    msg = i_to_s(chunk_number)
    print("Send Chunk number : ", msg)
    msg = str.encode(msg)
    sock.send(msg)
    act_cn = chunk_number - offset
    f.seek((act_cn-1)*CHUNK_SIZE)
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


    ack = sock.recv(MESSAGE_SIZE).decode()
    if ack[0] != '9':
        print("ERRR ERR ERRRRRRR")
        return -1
    print(f"{chunk_number} sent")
    return 0


def send_chunks(ip, port, chunks, file_name, offset):
    ssock = socket(AF_INET, SOCK_STREAM)
    ssock.connect((ip, port))
    f_name = f"T|{file_name}|"
    f_name = f_name + '\0'*(MESSAGE_SIZE - len(f_name))
    ssock.send(str.encode(f_name))
    num_chunks = i_to_s(len(chunks))
    ssock.send(str.encode(num_chunks))
    f = open(file_name, "rb")
    for chunk in chunks:
        v = send_single_chunk(f, ssock, chunk, offset)
        if v == -1:
            break
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
    offset = None
    for chunks, ip, port in parsed_details:
        chunk_nums = list(map(int, chunks.split(",")))
        if offset is None:
            offset = chunk_nums[0] - 1 #because i work with 1 based indexing.
        print("chunk nums : ", chunk_nums)
        thread = threading.Thread(target=send_chunks, args=[ip, port, chunk_nums, file_name, offset])
        thread.start()
        thread_list.append(thread)

    for thread in thread_list:
        thread.join()

    msg = "A|{}|".format(file_name)
    msg = msg + "\0"*(MESSAGE_SIZE - len(msg))
    send_sock.send(str.encode(msg))
    print("ACK Sent.")
    send_sock.close()

def upload_file(file_names):
    for file_name in file_names:
        upload_single_file(file_name)

def download_single_file(file_name) :
    recv_sock = socket()
    recv_sock.connect((MASTER_IP, MASTER_PORT))
    str_to_send = "|".join(["D", file_name, ""])
    str_to_send = str_to_send + '\0'*(MESSAGE_SIZE - len(str_to_send))
    str_bytes = str.encode(str_to_send)
    print(f"Sending {len(str_bytes)} of data.")
    recv_sock.send(str_bytes)
    details = recv_sock.recv(MESSAGE_SIZE).decode()
    print("I got ", details)
    parsed_details = command_parser.command_parser(details)
    chunk_server_details(parsed_details,file_name)
    recv_sock.close()

def download_file(file_names) :
    for file_name in file_names :
        download_single_file(file_name)

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
    elif command == "download" :
        download_file(inp[1:])
