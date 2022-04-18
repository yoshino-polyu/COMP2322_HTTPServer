# encoding: utf-8
from calendar import weekday
import os
import pathlib
import datetime
import time

# The status code
class get_status_line(object):
    OK = 'HTTP/1.1 200 OK\r\n'
    NOT_FOUND = 'HTTP/1.1 404 Not Found\r\n'
    BAD_REQUEST = 'HTTP/1.1 400 Bad Request\r\n'
    
# The content type
class content_type(object):
    HTML = 'Content-Type: text/html\r\n'
    PNG = 'Content-Type: img/png\r\n'
    JPG = 'Content-Type: img/jpg\r\n'

class resource_path(object):
    root_dir = str(pathlib.Path().resolve()) + '/htdocs' # root directory
    not_found_html = root_dir + '/' + '404.html' # 404 page
    bad_request_html = root_dir + '/' + '400.html' # 400 page

class http_request(object):
    def __init__(self):
        self.method = None
        self.url = None
        self.protocol = None
        self.status_line = get_status_line.OK
        self.response_head = content_type.HTML
        self.response_body = ''
    
    def parse_request(self, request : str):
        # print(type(request.split('\r\n', 1)))
        request_line = request.split('\r\n', 1)[0]
        header_list = request_line.split(' ')
        print("header_list:", header_list)
        self.method = header_list[0].upper()
        print("header_list[0]:", header_list[0])
        self.url = header_list[1]
        print("header_list[1]:", header_list[1])
        self.protocol = header_list[2]
        print("header_list[2]:", header_list[2])
        if self.method == 'GET' or self.method == 'HEAD':
            file_relative_path = self.url
            if self.url == '/':
                file_relative_path = '/index.html'
            file_path = resource_path.root_dir + file_relative_path
        else: # bad request
            self.status_line = get_status_line.BAD_REQUEST
            file_path = resource_path.bad_request_html
        self.handle_file_request(file_path, self.method)
    
    # handle the request
    def handle_file_request(self, file_path : str, method_type : str):
        # if cannot find the path, response with 404
        # 对于GET来说, 路径可以分为三种情况: 路径不存在、路径不是一个文件、路径是一个文件。
        if not os.path.isfile(file_path):
            f = open(resource_path.not_found_html, 'r')
            self.status_line = get_status_line.NOT_FOUND
            self.response_head = content_type.HTML
            self.response_body = f.read()
            f.close()
        else:
            extension = os.path.splitext(file_path)[1]
            # 图片资源需要使用二进制读取
            if extension == '.png' or extension == '.jpg':
                f = open(file_path, 'rb')
                if extension == '.png':
                    self.response_head = content_type.PNG
                else: # jpg
                    self.response_head = content_type.JPG
                # when load image from a file, it is in correct encoding already. 
                self.response_body = f.read()
                f.close()
            else: # request a html file
                f = open(file_path, 'r')
                self.response_head = content_type.HTML
                self.response_body = f.read()
                f.close()

        if self.status_line.split('\r\n')[0].split(' ')[-1] == 'OK':
            self.response_head += self.get_http_date(datetime.datetime.utcfromtimestamp(os.path.getmtime(file_path))) + '\r\n'
            
        if method_type == 'HEAD':
            self.response_body = ''
    
    def get_http_date(self, date_str : str):
        """
        Return a string representation of a date according to RFC 1123 (HTTP/1.1).
        The supplied date must be in UTC.
        """
        weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][date_str.weekday()]
        month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
             "Oct", "Nov", "Dec"][date_str.month - 1]
        return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (weekday, date_str.day, month, date_str.year, date_str.hour, date_str.minute, date_str.second)

    def get_response(self):
        if isinstance(self.response_body, str):
            return (self.status_line + self.response_head + '\r\n' + self.response_body).encode('utf-8')
        else: # self.response_body is 'bytes' type, which means the content is image. 
            return (self.status_line + self.response_head + '\r\n').encode('utf-8') + self.response_body
                