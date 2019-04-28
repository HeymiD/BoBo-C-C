import socket

def Main():
    host = '127.0.0.1'
    port = 12345
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((host,port))
    message = "Connected to Server"
    while True:
        s.send(message.encode('ascii'))
        data = s.recv(1024)
        print("Server:"  + str(data.decode('ascii')))
        answer = input('\nPress Y to continue N to quit')
        if answer == 'Y':
            continue
        else:
            break
    s.close()
if __name__ == '__main__':
    Main()