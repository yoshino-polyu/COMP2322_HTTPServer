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
        FL = open("log.txt", "w") # The file is created if it does not exist, otherwise it is truncated. 
        for i in self.log_list:
            FL.write("[")
            for j in i: # a specific list
                FL.write("'" + str(j) + "'" + ",")
            FL.write("]\n")
        FL.close()
    
    def load_file(self):
        try:
            FL = open("log.txt", "r", encoding="UTF-8")
            self.read_lines(FL)
        except FileNotFoundError:
            print("Load: File does not exist")
        finally:
            FL.close()
            print("Load: File Closed")

    def read_lines(self, FL : TextIOWrapper):
        for i in FL.readlines():
            try:
                eval(i)
            except SyntaxError:
                print("Illegal file format!")
                FL.close()
                return
            i = eval(i)
            for j in enumerate(i):
                if isinstance(j[1], str):
                    i[j[0]] = j[1]
            self.log_list.append(i)    

# def read_request(socket_in_connection):
#     """
#     use while true read the request message in case it is larger than 1kb. 
#     """
#     read_message = b"" #  'b' character before a string is used to specify the string as a “byte string“
#     while True:
#         tmp_message = socket_in_connection.recv(1024)# 1024 assumes the size of message read at most 1kb, but we can concatenate them to form a larger one. 
#         if tmp_message:
#             print("kkkk")
#             read_message += tmp_message
#         else:
#             print("bbbbbb")
#             break
#     return_message = read_message.decode()
#     # print("read message", read_message)
#     return return_message
    
class ClientService(threading.Thread):
    def __init__(self, socket_in_connection : socket, client_addr, mutex):
        """
        @param client_addr: the address bound to the socket on the other end of the connection.
        @param mutex: lock object
        """
        super(ClientService, self).__init__()
        self.socket_in_connection = socket_in_connection
        self.client_addr = client_addr
        self.mutex = mutex
    def run(self):
        """
        @summary: Override the run method
        """
        keep_alive_timeout = 15.0 # just listens to the new client and ends when it doesn't talk for 15 seconds. 
        # server_log = http_server()
        # The timeout applies independently to each call to socket read/write operation.
        self.socket_in_connection.settimeout(keep_alive_timeout)
        
        while True:
            try:
                # every time receive the data, reset the timeout. 
                    # request = ""
                    # request = read_request(socket_in_connection)
                request = self.socket_in_connection.recv(1024).decode() # 1024 assumes the size of message < 1kb. 
                access_time = ""
                tmp = http_request.get_http_date(datetime.datetime.utcnow()).split(',')
                for i in tmp:
                    access_time += i
                requested_file_name = http_request.get_requested_file_name(request)
                if requested_file_name == '':
                    requested_file_name = "index.html"
                
                http_req = http_request()
                http_req.parse_request(request)
                self.socket_in_connection.sendall(http_req.get_response()) # send response to client 
                response_type = http_req.get_response_type()
                
                info_list = []
                info_list.append(self.client_addr[0]) # addr[0] is the ip address
                info_list.append(access_time)
                info_list.append(requested_file_name)
                info_list.append(response_type)
                # synchronize IO operations. 
                self.mutex.acquire()
                server_log = http_server()
                server_log.log_list.append(info_list)
                server_log.write_file()
                del server_log # remove the object from memory
                self.mutex.release()
                
                if not http_req.is_keep_alive: # one-time transfer of data. 
                    break

            # Exception to handle timeout exception.
            except Exception as e: 
                print("Keep alive timeout. Disconnected.")
                self.socket_in_connection.close()
                break

        self.socket_in_connection.close()

def main():
    # Define socket host and port
    SERVER_HOST = '127.0.0.1'
    SERVER_PORT = 8000

    # socket.AF_INET -> an address family that is used to designate the type of addresses that your socket can communicate with (in this case, Internet Protocol v4 addresses)
    # Create socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    # bind port
    server_socket.bind((SERVER_HOST, SERVER_PORT)) 
    # set up a listener
    server_socket.listen(128) # server socket is used to listening on port
    print('Listening on port %s' % SERVER_PORT)
    lock = threading.Lock() # lock the IO of log.txt
    while True:
        # Wait for client connections
        client_connection, client_address = server_socket.accept()
        """
        https://docs.python.org/3/library/socket.html#socket-objects
        The return value is a pair (conn, address) where conn is a new socket object 
        usable to send and receive data on the connection, 
        and address is the address bound to the socket on the other end of the connection.
        """
        # Use a thread per client to avoid the blocking client.recv() then use the main thread just for listening for new clients. 
        p = ClientService(client_connection, client_address, lock)
        p.start() # start the thread.
    server_socket.close() # dont close to achieve several rounds of communication in one TCP connection. 

if __name__ == '__main__':
    main()