import socket
import threading
from httphead import http_request
import pathlib

def service_client(new_socket, addr):
    print("Accept new connection from %s:%s..." % addr)
    request = new_socket.recv(1024).decode()
    print("the request content: \n" + request)
    http_req = http_request()
    http_req.parse_request(request)
    new_socket.sendall(http_req.get_response())
    new_socket.close()
    
def main():
    # Define socket host and port
    SERVER_HOST = '127.0.0.1'
    SERVER_PORT = 8000

    # Create socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    # bind port
    server_socket.bind((SERVER_HOST, SERVER_PORT)) 
    # 设置监听
    server_socket.listen(128)
    print('Listening on port %s' % SERVER_PORT)

    while True:
        # Wait for client connections
        client_connection, client_address = server_socket.accept()
        # Thread object is used to create threads. 
        p = threading.Thread(target=service_client, args=(client_connection,client_address))
        p.start() # start the thread. 
        # break
    server_socket.close()

if __name__ == '__main__':
    print(pathlib.Path().resolve())
    main()
