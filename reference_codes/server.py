import socket
sock = socket.socket()

sock.bind(("127.0.0.1", 12345))

sock.listen(5)

#will accept only one connection at a time
client_sock, client_addr = sock.accept()

message = b"This is sent by the server."

client_sock.send(message)

client_sock.close()
sock.close()
