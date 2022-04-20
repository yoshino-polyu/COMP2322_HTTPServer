import socket
import threading
from httphead import http_request

def service_client(new_socket, addr):
    print("Accept new connection from %s:%s..." % addr)
    keep_alive_timeout = 100.0
    # The timeout applies independently to each call to socket read/write operation.
    new_socket.settimeout(keep_alive_timeout)
    while True:
        try:
            # every time receive the data, reset the timeout. 
            request = new_socket.recv(1024).decode()
            print("!!!!!the request content: \n" + request)
            http_req = http_request()
            http_req.parse_request(request)
            new_socket.sendall(http_req.get_response())

            if not http_req.is_keep_alive: # one-time transfer of data. 
                print("is_keep_alive: ", http_req.is_keep_alive)
                break

        except Exception as e: # Exception to handle timeout exception.
            print("Keep alive timeout. Disconnected.")
            new_socket.close()
            break

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
    main()
