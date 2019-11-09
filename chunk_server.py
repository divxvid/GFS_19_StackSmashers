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

def process_request(csock, caddr):
    msg = csock.recv(1024).decode()
    print("I got ", msg)
    csock.close()
    
list_sock = socket()
list_sock.bind((MY_IP, MY_PORT))
list_sock.listen(10)

while True:
    csock, caddr = list_sock.accept() 
    thrd = threading.Thread(target=process_request, args=[csock, caddr])
    thrd.start()

list_sock.close()
