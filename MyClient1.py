# a simple HTTP client
import socket

SERVER_HOST = '127.0.0.1' 
SERVER_PORT = 8000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
client_socket.connect((SERVER_HOST, SERVER_PORT))
request = input('Input HTTP request command:\n') 
client_socket.send(request.encode())
response = client_socket.recv(1024) 
print ('Server response:\n')
print (response.decode()) 
client_socket.close()