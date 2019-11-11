'''
FILE -> CHUNK(512K) -> parts(1024 bytes)
'''

import socket

CHUNK_SIZE = 512 * 1024
BLOCK_SIZE = 1024

def s_to_i(msg):
    parts = msg.split("|")
    return int(parts[1])

sock = socket.socket()
sock.bind(("127.0.0.1", 6969))
sock.listen(10)
csock, caddr = sock.accept()

n_chunks = csock.recv(BLOCK_SIZE).decode()
n_chunks = s_to_i(n_chunks)
print("n_chunks", n_chunks)
for i in range(n_chunks):
    print("Starting receive for chunk", i)
    f = open(f"chunk{i}.chunk", "wb")
    n_blocks = csock.recv(BLOCK_SIZE).decode()
    n_blocks = s_to_i(n_blocks)
    print("n_blocks : ", n_blocks)
    for _ in range(n_blocks):
        data = csock.recv(BLOCK_SIZE)
        f.write(data)
    r_blocks = csock.recv(BLOCK_SIZE).decode()
    r_blocks = s_to_i(r_blocks)
    print("r_Blocks : ", r_blocks)
    if r_blocks == 0:
        continue
    data = csock.recv(r_blocks)
    f.write(data)
    f.close()
    print("Chunk {} written.".format(i))

