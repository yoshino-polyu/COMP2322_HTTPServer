from io import TextIOWrapper
import socket
import threading
from httphead import http_request
import datetime
from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE, SelectorKey

selector = DefaultSelector()
lock = threading.Lock() # lock the IO of log.txt
KEEP_ALIVE_TIMEOUT = 15.0 # just listens to the new client and ends when it doesn't talk for 15 seconds. 

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
    

class ClientService(threading.Thread):
    def __init__(self, socket_in_connection : socket.socket, client_addr, mutex : threading.Lock):
        """
        @param client_addr: the address bound to the socket on the other end of the connection.
        @param mutex: lock object
        """
        super(ClientService, self).__init__()
        self.socket_in_connection = socket_in_connection
        self.socket_in_connection.setblocking(False)
        self.socket_in_connection.settimeout(KEEP_ALIVE_TIMEOUT) # every time receive the data, the timeout will be reset.
        self.client_addr = client_addr
        self.mutex = mutex
        
    # def read_buf(self, key : SelectorKey):
    #     """
    #     call back for read event
    #     """
    #     selector.unregister(key.fd)
    
    def run(self):
        """
        @summary: Override the run method
        """
        while True:
            try:
                # self.socket_in_connection.setblocking(False)
                # selector.register(self.socket_in_connection.fileno(), EVENT_READ, self.read_buf)

                self.request = self.socket_in_connection.recv(1024).decode() # 1024 assumes the size of message < 1kb. 
                
                access_time = ""
                rfc1123_date = http_request.get_http_date(datetime.datetime.utcnow()).split(',')
                for i in rfc1123_date:
                    access_time += i
                
                requested_file_name = http_request.get_requested_file_name(self.request)
                if requested_file_name == '':
                    requested_file_name = "index.html"
                
                http_req = http_request()
                http_req.parse_request(self.request)
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

def accept(listening_socket : socket.socket, mask):
    """
    Callback for new connections
    """
    client_connection, client_address = listening_socket.accept()
    print("accept{}".format(client_address))
    # client_connection.setblocking(False)
    p = ClientService(client_connection, client_address, lock)
    p.start()
    selector.unregister(listening_socket)

def main():
    # Define socket host and port
    SERVER_HOST = '127.0.0.1'
    SERVER_PORT = 8000

    # socket.AF_INET -> an address family that is used to designate the type of addresses that your socket can communicate with (in this case, Internet Protocol v4 addresses)
    # Create socket
    listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    listening_socket.setblocking(False) # non-blocking socket
    # bind port
    listening_socket.bind((SERVER_HOST, SERVER_PORT)) 
    # set up a listener
    listening_socket.listen(128) # server socket is used to listening on port
    print('Listening on port %s' % SERVER_PORT)

    selector.register(listening_socket.fileno(), EVENT_READ, accept)

    while True:
        print("Waiting for I/O")
        """
        In the multiplexing model, for each socket, it is generally set to be non-blocking, but, as shown below, 
        the entire user's process is actually blocked all the time. 
        Only the process is blocked by the select function, not by the socket IO.
        """
        ready = selector.select() # blocking select()
        for key, mask in ready:
            callback = key.data
            callback(key.fileobj, mask)
            """
            Socket descriptors are file system handles, and should be unique to your process for the duration of it's session
            https://stackoverflow.com/questions/28031326/are-socket-descriptor-unique#:~:text=Socket%20descriptors%20are%20file%20system,the%20duration%20of%20it's%20session.
            """
            if key.fd == listening_socket.fileno():
                selector.register(listening_socket.fileno(), EVENT_READ, accept)

    # while True:
    #     # Wait for client connections
    #     client_connection, client_address = server_socket.accept()
    #     """
    #     https://docs.python.org/3/library/socket.html#socket-objects
    #     The return value is a pair (conn, address) where conn is a new socket object 
    #     usable to send and receive data on the connection, 
    #     and address is the address bound to the socket on the other end of the connection.
    #     """
    #     # Use a thread per client to avoid the blocking client.recv() then use the main thread just for listening for new clients. 
    #     p = ClientService(client_connection, client_address, lock)
    #     # print("p is {}".format(p))
    #     p.start() # start the thread.
    # server_socket.close() # dont close to achieve several rounds of communication in one TCP connection. 

if __name__ == '__main__':
    main()

#
# https://www.cnblogs.com/russellyoung/p/python-zhiio-duo-lu-fu-yong.html 
#