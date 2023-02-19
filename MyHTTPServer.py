from io import TextIOWrapper
import socket
import threading
import asyncio
from asyncio import StreamReader, StreamWriter
from concurrent.futures import ThreadPoolExecutor
from httphead import http_request
import datetime
from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE, SelectorKey
from functools import partial

CHUNK_LIMIT = 1024

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


# class ClientService(threading.Thread):
#     def __init__(self, socket_in_connection : socket.socket, client_addr, mutex : threading.Lock):
#         """
#         @param client_addr: the address bound to the socket on the other end of the connection.
#         @param mutex: lock object
#         """
#         super(ClientService, self).__init__()
#         self.socket_in_connection = socket_in_connection
#         self.socket_in_connection.setblocking(False)
#         self.socket_in_connection.settimeout(KEEP_ALIVE_TIMEOUT) # every time receive the data, the timeout will be reset.
#         self.client_addr = client_addr
#         self.mutex = mutex
        
#     # def read_buf(self, key : SelectorKey):
#     #     """
#     #     call back for read event
#     #     """
#     #     selector.unregister(key.fd)
#     @coroutine
#     def run(self):
#         """
#         @summary: Override the run method
#         """
#         while True:
#             try:
#                 # self.socket_in_connection.setblocking(False)
#                 # selector.register(self.socket_in_connection.fileno(), EVENT_READ, self.read_buf)

#                 self.request = self.socket_in_connection.recv(1024).decode() # 1024 assumes the size of message < 1kb. 
                
#                 access_time = ""
#                 rfc1123_date = http_request.get_http_date(datetime.datetime.utcnow()).split(',')
#                 for i in rfc1123_date:
#                     access_time += i
                
#                 requested_file_name = http_request.get_requested_file_name(self.request)
#                 if requested_file_name == '':
#                     requested_file_name = "index.html"
                
#                 http_req = http_request()
#                 http_req.parse_request(self.request)
#                 self.socket_in_connection.sendall(http_req.get_response()) # send response to client 
#                 response_type = http_req.get_response_type()
                
#                 info_list = []
#                 info_list.append(self.client_addr[0]) # addr[0] is the ip address
#                 info_list.append(access_time)
#                 info_list.append(requested_file_name)
#                 info_list.append(response_type)
                
#                 # synchronize IO operations. 
#                 self.mutex.acquire()
#                 server_log = http_server()
#                 server_log.log_list.append(info_list)
#                 server_log.write_file()
#                 del server_log # remove the object from memory
#                 self.mutex.release()
                
#                 if not http_req.is_keep_alive: # one-time transfer of data. 
#                     break

#             # Exception to handle timeout exception.
#             except Exception as e: 
#                 print("Keep alive timeout. Disconnected.")
#                 self.socket_in_connection.close()
#                 break
#         self.socket_in_connection.close()


# stuff_lock = asyncio.Lock() # asyncio.Lcok allows you to protect a critical section, without blocking other coroutines from running which don't need access to that critical section.
# q = asyncio.Queue(16) # 需要注意协程的消息队列需要使用asyncio.Queue，普通queue无法使用await
    
# def process_msg(request : str, client_IP : str):
#     access_time = ""
#     rfc1123_date = http_request.get_http_date(datetime.datetime.utcnow()).split(',')
#     for i in rfc1123_date:
#         access_time += i
#     requested_file_name = http_request.get_requested_file_name(request)
#     if requested_file_name == '':
#         requested_file_name = 'index.html'
#     http_req = http_request()
#     http_req.parse_request(request)
#     response_type = http_req.get_response_type()
    
#     info_list = []
#     info_list.append(client_IP)
#     info_list.append(access_time)
#     info_list.append(requested_file_name)
#     info_list.append(response_type)
    
#     # async with stuff_lock: # TODO: check whether it is necessary. if add, the return type will be coroutine. 
#     server_log = http_server()
#     server_log.log_list.append(info_list)
#     server_log.write_file()
#     del server_log
#     return http_req.get_response()

# async def read_msg(reader):
#     request = (await reader.read(1024)).decode()
#     return request

# async def write_msg(writer : StreamWriter, response : str):
#     writer.write(response)
#     await writer.drain()
#     return

# good blog: https://stackoverflow.com/questions/48506460/python-simple-socket-client-server-using-asyncio
# async def recv_process(reader : StreamReader, writer : StreamWriter):
#     while True:
#         try:
#             rmsg = await read_msg(reader) # 如果socket上没有数据过来，则内部调用yield让出CPU并block在此处
#             print("rmsg = ", rmsg)
#             wmsg = process_msg(rmsg, writer.get_extra_info('peername')[0]) # 用来处理客户端发送过来的数据
#             print("wmsg = ", wmsg)
#             print("type = ", type(wmsg))
#             if q.full():
#                 print('queue is full, pop oldest msg and append new msg')
#                 q.get_nowait() # 如果消息队列已经存满，则删除最早的信息
#                 q.put_nowait(wmsg)
#                 print('queue now size', q.qsize())
#             else:
#                 q.put_nowait(wmsg)
#                 print('queue now size', q.qsize())
#         except BaseException as e:
#             print("recv_process exception", e)
#             return # 如果发生异常（一般常见于客户端发送socket close）则退出循环

# async def send_process(reader : StreamReader, writer : StreamWriter):
#     print("bbbbbbbbb")
#     while True:
#         try:
#             print("kkkkkkkkkk")
#             wmsg = await q.get()
#             print("========================================")
#             print("wmsg = ", wmsg)
#             print("type = ", type(wmsg))
#             print("queue left size: ", q.qsize())
#             await write_msg(writer, wmsg)
#         except BaseException as e:
#             print("send_process exception:", e) # 如果发生异常（一般常见于客户端接收socket close）则退出循环
#             return

async def build_response(request : str, client_IP : str):
    access_time = ""
    rfc1123_date = http_request.get_http_date(datetime.datetime.utcnow()).split(',')
    for i in rfc1123_date:
        access_time += i
    requested_file_name = http_request.get_requested_file_name(request)
    if requested_file_name == '':
        requested_file_name = 'index.html'
    http_req = http_request()
    http_req.parse_request(request)
    response_type = http_req.get_response_type()
    
    info_list = []
    info_list.append(client_IP)
    info_list.append(access_time)
    info_list.append(requested_file_name)
    info_list.append(response_type)
    
    # async with stuff_lock: # TODO: check whether it is necessary. if add, the return type will be coroutine. 
    server_log = http_server()
    server_log.log_list.append(info_list)
    server_log.write_file()
    del server_log
    await asyncio.sleep(0) # trick
    return http_req.get_response()

async def read_request(socket_in_connection : socket.socket):
    print("fuckfuck")
    request = (await loop.sock_recv(socket_in_connection, CHUNK_LIMIT)).decode('utf8')
    # while True:
    #     chunk = (await loop.sock_recv(socket_in_connection, CHUNK_LIMIT)).decode('utf8')
    #     request += chunk
    #     if len(chunk) < CHUNK_LIMIT:
    #         break
    print(f"request = {request}")
    return request

async def handle_client(socket_in_connection: socket.socket, client_addr):
    request = await read_request(socket_in_connection)
    print("request = ", request)
    response = await build_response(request, client_addr)
    print("response = ", response)
    await loop.sock_sendall(socket_in_connection, response)
    socket_in_connection.close()

async def run_server(listening_socket):
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor()
    while True:
        print(f"listening on port: {SERVER_PORT}")
        socket_in_connection, client_addr = await loop.sock_accept(listening_socket)
        print("kkkkkkk")
        print(f"socket_in_connection = {socket_in_connection}, client_addr = {client_addr}")
        loop.run_in_executor(executor, partial(handle_client, socket_in_connection, client_addr))
        # loop.create_task(handle_client(socket_in_connection, client_addr))

# 1：服务器接收客户端发送过来的数据
# 2：服务器进行AI运算，把运算结果保存到消息队列
# 3：服务器从消息队列中读取AI运算之后结果
# 4：服务器发送处理过的数据给客户端

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 8000

SERVER_PORT_SEND = 7777


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen(128)

loop = asyncio.get_event_loop() # 用来挂协程
loop.run_until_complete(run_server(server_socket))
# (run_server(server_socket))

# loop.run_forever()
# loop.run_until_complete(run_server(server_socket))
# try:

# except KeyboardInterrupt:
#     server_socket.close()

# # 创建协程服务，callback分别是前面的recv_process和send_process，然后指定服务的host，port和挂协程的loop
# routine_recv = asyncio.start_server(recv_process, SERVER_HOST, SERVER_PORT, loop=loop)
# routine_send = asyncio.start_server(send_process, SERVER_HOST, SERVER_PORT_SEND, loop=loop)

# # coroutine = [routine_recv, routine_send]
# # run_until_complete方法内部会把传进这个方法的协程coro给封装为Task对象（run_forever也会），然后再放到任务列表中。
# server_recv, server_send = loop.run_until_complete(asyncio.gather(routine_recv, routine_send))

# print('Recv server running on:', format(server_recv.sockets[0].getsockname()))
# print('Send server running on:', format(server_send.sockets[0].getsockname()))

# try:
#     print("at forever")
#     loop.run_forever()
# # 这个地方很重要，如果客户端的read/write socket异常关闭了，

# # 正常情况下loop上绑定的协程就退出了while True循环，接着也就退出了整个main函数

# # 但是作为一个服务器，我们并不希望main函数就这么退出了，所以就有了run_forever

# # 这个函数的意思是当loop上的协程退出之后继续运行，然后重新创建socket等待下一次连接
# except KeyboardInterrupt:
#     pass
# server_recv.close()
# loop.run_until_complete(server_recv.wait_closed())
# server_send.close()
# loop.run_until_complete(server_send.wait_closed())# 关闭协程
# loop.close()




#
# https://www.cnblogs.com/russellyoung/p/python-zhiio-duo-lu-fu-yong.html 
#