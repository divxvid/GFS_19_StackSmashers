import socket
sock = socket.socket()

sock.connect(("127.0.0.1", 12346))

filenew=open("score.mp3","wb")

packet=sock.recv(1024)
while packet:
	filenew.write(packet)
	packet=sock.recv(1024)

sock.close()
