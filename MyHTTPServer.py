from io import TextIOWrapper
import socket
import threading
from httphead import http_request
import datetime

class http_server(object):
    """
    This class is mainly used to handle the IO of log file. 
    """
    def __init__(self):
        self.log_list = [] # [Client IP address,Access Time,Requested File Name,Response Type]
        self.load_file()
    
    def write_file(self):
        FL = open("log.txt", "w")
        for i in self.log_list:
            FL.write("[")
            for j in i: # a specific list
                FL.write("'" + str(j) + "'" + ",")
            FL.write("]\n")
        FL.close()
    
    def load_file(self):
        FL = open("log.txt", "r", encoding="UTF-8")
        self.read_lines(FL)
    
    def read_lines(self, FL : TextIOWrapper):
        for i in FL.readlines():
            try:
                eval(i)
            except SyntaxError:
                FL.close()
                return
            i = eval(i)
            for j in enumerate(i):
                if isinstance(j[1], str):
                    i[j[0]] = j[1]
            self.log_list.append(i)    

def service_client(new_socket, addr, mutex):
    """
    Parses the request and obtains the corresponding response message. 
    """
    
    # add the client's ip address.
    
    keep_alive_timeout = 15.0
    # server_log = http_server()
    # The timeout applies independently to each call to socket read/write operation.
    new_socket.settimeout(keep_alive_timeout)

    while True:
        try:
            c = 10
            # every time receive the data, reset the timeout. 
            request = new_socket.recv(1024).decode()
            access_time = ""
            tmp = http_request.get_http_date(datetime.datetime.utcnow()).split(',')
            for i in tmp:
                access_time += i
            
            requested_file_name = http_request.get_requested_file_name(request)
            if requested_file_name == '':
                requested_file_name = "index.html"
            
            http_req = http_request()
            http_req.parse_request(request)
            new_socket.sendall(http_req.get_response())
            response_type = http_req.get_response_type()
            
            info_list = []
            info_list.append(addr[0]) # addr[0] is the ip address
            info_list.append(access_time)
            info_list.append(requested_file_name)
            info_list.append(response_type)
            
            mutex.acquire()
            server_log = http_server()
            server_log.log_list.append(info_list)
            server_log.write_file()
            del server_log # remove the object from memory
            mutex.release()
            
            if not http_req.is_keep_alive: # one-time transfer of data. 
                break

        # Exception to handle timeout exception.
        except Exception as e: 
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
    # set up a listener
    server_socket.listen(128)
    print('Listening on port %s' % SERVER_PORT)
    lock = threading.Lock() # lock the IO of log.txt
    while True:
        # Wait for client connections
        client_connection, client_address = server_socket.accept()
        # Thread object is used to create threads. 
        p = threading.Thread(target=service_client, args=(client_connection,client_address, lock))
        p.start() # start the thread.
    server_socket.close()


if __name__ == '__main__':
    main()
