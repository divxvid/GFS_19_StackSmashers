from socket import socket
import sys
import threading

#     COMMANDLINE PARSING
argc = len(sys.argv)
MY_IP, MY_PORT = "", 33333

print(sys.argv)
if argc < 2:
    print("Invalid launch options.")
    sys.exit()

if argc == 3:
    MY_IP = sys.argv[1].strip()
MY_PORT = int(sys.argv[-1].strip())
#     COMMANDLINE PARSING END

MESSAGE_SIZE = 1024
CHUNK_SIZE = 512 * 1024

def s_to_i(msg):
    parts = msg.split("|")
    if parts[0] == "N":
        return int(parts[1])
    return None

def extract_string(msg):
    parts = msg.split("|")
    if parts[0] == "T":
        return parts[1]
    return None

def process_request(csock, caddr):
    file_name = csock.recv(MESSAGE_SIZE).decode()
    file_name = extract_string(file_name)
    n_chunks = csock.recv(MESSAGE_SIZE).decode()
    n_chunks = s_to_i(n_chunks)
    print("n_chunks", n_chunks)
    for ppp in range(n_chunks):
        i = csock.recv(MESSAGE_SIZE).decode()
        i = s_to_i(i)
        print("Starting receive for chunk", i)
        f = open(f"{file_name}{i}.chunk", "wb")
        read_size = csock.recv(MESSAGE_SIZE).decode()
        read_size = s_to_i(read_size)
        while read_size > 0:
            dr = csock.recv(MESSAGE_SIZE)
            f.write(dr)
            read_size -= len(dr)

        f.close()
        print("Chunk {} written.".format(i))
    csock.close()

list_sock = socket()
list_sock.bind((MY_IP, MY_PORT))
list_sock.listen(10)

while True:
    csock, caddr = list_sock.accept()
    thrd = threading.Thread(target=process_request, args=[csock, caddr])
    thrd.start()

list_sock.close()
