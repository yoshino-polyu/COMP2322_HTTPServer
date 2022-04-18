# encoding: utf-8
from calendar import weekday
from email import header
import os
import pathlib
import datetime

# The status code
class get_status_line(object):
    OK = 'HTTP/1.1 200 OK\r\n'
    NOT_MODIFIED = 'HTTP/1.1 304 Not Modified\r\n'
    NOT_FOUND = 'HTTP/1.1 404 Not Found\r\n'
    BAD_REQUEST = 'HTTP/1.1 400 Bad Request\r\n'
    
# The content type
class content_type(object):
    HTML = 'Content-Type: text/html\r\n'
    PNG = 'Content-Type: img/png\r\n'
    JPG = 'Content-Type: img/jpg\r\n'

# The path of html server resource
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
        self.is_keep_alive = False
    
    @staticmethod
    def parse_request_head(request : str):
        """
        Returns the three entries of request line and a map of message header. 
        """
        # removing both the leading and trailing space of request
        request = request.strip()
        # find the index of the first occurrence of '\r\n'
        first_break = request.find('\r\n')
        http_method, url, protocol = request[:first_break].split(' ')
        header_list = request.split('\r\n')
        header_dict = {}
        for header in header_list:
            # find returns -1 if ': ' is not found. 
            if header.find(': ') != -1:
                k, v = header.split(': ')
                header_dict[k.lower()] = v
        return http_method.upper(), url, protocol, header_dict
        
    def parse_request(self, request : str):
        """
        Obtains the corresponding file path for retrieving content. 
        Delivers file path, request method, map of message header and a sign 
        of bad request to handle_file_request()
        """
        if request == '':
            return
        self.method, self.url, self.protocol, header_dict = self.parse_request_head(request)
        
        if 'connection' in header_dict and header_dict['connection'] == 'keep-alive':
            self.is_keep_alive = True

        # if it is not GET and HEAD, then it is a bad request, which means
        # it is not a supported syntax, so set bad request
        is_bad_req = False
        if self.method == 'GET' or self.method == 'HEAD':
            file_relative_path = self.url
            if self.url == '/':
                file_relative_path = '/index.html'
            file_path = resource_path.root_dir + file_relative_path
        else: # bad request
            is_bad_req = True # whether is a bad request. 
            file_path = resource_path.bad_request_html
        self.handle_file_request(file_path, self.method, header_dict, is_bad_req)
    
    def handle_file_request(self, file_path : str, method_type : str, header_dict, is_bad_req):
        if is_bad_req:
            self.status_line = get_status_line.BAD_REQUEST
        
        self.response_head += 'datetime: '
        self.response_head += self.get_http_date(datetime.datetime.utcnow()) + '\r\n'

        # if cannot find the path, response with 404
        # For GET/HEAD, there are three cases: the path does not exist, 
        # the path is not a file, and the path is a file. 
        
        # Paths that do not exist and paths that are not a file can be discussed in one category, 
        # and paths that are a file that exist can be discussed in another category. 
        if not os.path.isfile(file_path):
            f = open(resource_path.not_found_html, 'r')
            self.status_line = get_status_line.NOT_FOUND
            self.response_head += content_type.HTML
            self.response_body = f.read() 
            f.close()
        else:
            if not is_bad_req:
                # if not a bad request, always return the last-modified entry. 
                self.response_head += 'last-modified: '
                self.response_head += self.get_http_date(datetime.datetime.utcfromtimestamp(os.path.getmtime(file_path))) + '\r\n'
            
            # the following conditions are always true in HTTP/1.1
            if 'connection' in header_dict and header_dict['connection'] == 'keep-alive':
                self.response_head += 'keep-alive: timeout=10\r\n'
                
            if not is_bad_req  and 'if-modified-since' in header_dict:
                since_time = header_dict['if-modified-since']
                since_time = datetime.datetime.strptime(since_time, '%a, %d %b %Y %H:%M:%S GMT').timestamp()
                # modified_time is actually the last modified time of the specific file with path file_path
                modified_time = datetime.datetime.utcfromtimestamp(os.path.getmtime(file_path)).timestamp()
                if since_time >= modified_time:
                    self.status_line = get_status_line.NOT_MODIFIED
                    self.response_body = ''
                    return
            
            extension = os.path.splitext(file_path)[1]
            if extension == '.png' or extension == '.jpg':
                f = open(file_path, 'rb')
                if extension == '.png':
                    self.response_head += content_type.PNG
                else: # jpg
                    self.response_head += content_type.JPG
                # when load image from a file, it is in correct encoding already. 
                # Image resources need to be read as binary format.
                self.response_body = f.read() # return a byte type.
                f.close()
            else: # request a html file
                f = open(file_path, 'r')
                self.response_head += content_type.HTML
                self.response_body = f.read()
                f.close()
        
        # if not os.path.isfile(file_path):
        #     f = open(resource_path.not_found_html, 'r')
        #     self.status_line = get_status_line.NOT_FOUND
        #     self.response_head += content_type.HTML
        #     self.response_body = f.read() 
        #     f.close()
        # else:
        #     extension = os.path.splitext(file_path)[1]
        #     # 图片资源需要使用二进制读取
        #     if extension == '.png' or extension == '.jpg':
        #         f = open(file_path, 'rb')
        #         if extension == '.png':
        #             self.response_head += content_type.PNG
        #         else: # jpg
        #             self.response_head += content_type.JPG
        #         # when load image from a file, it is in correct encoding already. 
        #         self.response_body = f.read()
        #         f.close()
        #     else: # request a html file
        #         f = open(file_path, 'r')
        #         self.response_head += content_type.HTML
        #         self.response_body = f.read()
        #         f.close()
        
                # if method_type == 'HEAD' and :
                #     self.response_body = ''
                #     return
    
    def get_http_date(self, utc_date : datetime):
        """
        Return a string representation of a date according to RFC 1123 (HTTP/1.1).
        The supplied date must be in UTC.
        """
        weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][utc_date.weekday()]
        month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
             "Oct", "Nov", "Dec"][utc_date.month - 1]
        return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (weekday, utc_date.day, month, utc_date.year, utc_date.hour, utc_date.minute, utc_date.second)

    def get_response(self):
        if isinstance(self.response_body, str):
            return (self.status_line + self.response_head + '\r\n' + self.response_body).encode('utf-8')
        else: # self.response_body is 'bytes' type, which means the content is image. 
            return (self.status_line + self.response_head + '\r\n').encode('utf-8') + self.response_body
                