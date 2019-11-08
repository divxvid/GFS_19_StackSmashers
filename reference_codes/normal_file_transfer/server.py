import socket
sock = socket.socket()

sock.bind(("127.0.0.1", 12346))

sock.listen(5)

#will accept only one connection at a time
client_sock, client_addr = sock.accept()

file=open("SIX.mp3","rb")
packet=file.read(1024)
while packet:
	client_sock.send(packet)
	packet=file.read(1024)



client_sock.close()
sock.close()
