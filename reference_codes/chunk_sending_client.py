from socket import socket
from os.path import getsize
from math import ceil

CHUNK_SIZE = 512 * 1024
BLOCK_SIZE = 1024

def i_to_s(x):
    msg = f"N|{x}|"
    msg = msg + '\0' * (BLOCK_SIZE - len(msg))
    return msg

sock = socket()
sock.connect(("127.0.0.1", 6969))

file_name = "image.jpg"

with open(file_name, "rb") as f:
    file_size = getsize(file_name)
    n_chunks = ceil(file_size / CHUNK_SIZE)
    msg = i_to_s(n_chunks)
    msg = str.encode(msg)
    sock.send(msg) #number of chunks are sent now.
    for i in range(n_chunks):
        c_data = f.read(CHUNK_SIZE)
        read_size = len(c_data)
        n_blocks = read_size // BLOCK_SIZE
        r_block = read_size % BLOCK_SIZE
        msg = i_to_s(n_blocks)
        msg = str.encode(msg)
        sock.send(msg) # number of 1024 blocks.
        for j in range(n_blocks):
            base = j * 1024
            data = c_data[base:base+BLOCK_SIZE]
            sock.send(data) # sent the actual block(data)

        msg = i_to_s(r_block)
        msg = str.encode(msg)
        sock.send(msg)
        print("chunk {} sent.".format(i))
        if r_block == 0:
            continue
        data = c_data[-r_block:]
        sock.send(data)

