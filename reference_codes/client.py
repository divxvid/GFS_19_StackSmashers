import socket
sock = socket.socket()

sock.connect(("127.0.0.1", 12345))

message = sock.recv(1024)

print("I got : ", message)

sock.close()
