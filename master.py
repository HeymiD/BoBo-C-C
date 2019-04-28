
import socket
from _thread import *
import threading

print_lock = threading.Lock()

# thread fuction
def client_thread(client):
	while True:
		# data received from client
		data = client.recv(1024)
		if not data:
			print('Bye')

			# lock released on exit
			print_lock.release()
			break

		mes= "Recieved:\n"
		data =  mes.encode('ascii')+ data
		client.send(data)

	# connection closed
	client.close()


def Main():

	clients=[]

	host = ""

	# reverse a port on your computer
	# in our case it is 12345 but it
	# can be anything
	port = 12345
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((host, port))
	print("socket binded to post", port)

	# put the socket into listening mode
	s.listen(5)
	print("socket is listening")

	# a forever loop until client wants to exit
	while True:

		# establish connection with client
		client, addr = s.accept()

		# lock acquired by client
		print_lock.acquire()
		print('Connected to :', addr[0], ':', addr[1])

		# Start a new thread and return its identifier
		clients.add(start_new_thread(client_thread, (client,)))
		print clients
	s.close()


if __name__ == '__main__':
	Main()
