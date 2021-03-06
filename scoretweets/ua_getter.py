from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote
from threading import Thread
import time

POOL_DELAY = .1 # sec
TIMEOUT = 300 # sec
_ua_list = []

class DaemonThread(Thread):
    def __init__(self, func, *args):
        super().__init__(target=func, args=tuple(args))
        self.daemon = True

class HTTPRequestHandler(BaseHTTPRequestHandler):    
    def log_request(self, *args):
        pass # No need to log

    def parse_get_requestx(self):
        txt = self.requestline[4:-9]
        params = dict()
        path_params = txt.split('?')
        if len(path_params) == 1:
            return path_params[0], params
        path, params_up = path_params
        
        for i in params_up.split('&'):
            kv = i.split('=')
            k, v = (kv[0], None) if len(kv)==1 else kv
            params[unquote(k)]= unquote(v)
        return path, params
    
    def send_responsex(self, body, r_code=200):
        if isinstance(body, str):
            if not body.endswith('\n'):
                body += '\n'
            body = body.encode('utf-8')
            content_type = 'text/plain'
        else:
            content_type = 'text/html'
        
        self.send_response(r_code)
        self.send_header('Content-Type', content_type)
        self.end_headers()
        
        self.wfile.write(body)

    def handle_get_requestx(self):
        path, _ = self.parse_get_requestx()

        if path == '/':
            ua = self.headers.get('User-Agent')
            if ua:
                self.send_responsex(f'Found User-Agent: {ua}\nYou can go back to the program now.')
            else:
                self.send_responsex('Unable to find User-Agent.\nThe browser is not sending User-Agent header.', 400)
            _ua_list.append(ua)
        else:
            self.send_responsex('Not Found.', 404)

    def do_GET(self):
        self.handle_get_requestx()

class UAGetter:
    def __init__(self):
        self.__set_server()
        self.__will_serve = False

    def __set_server(self):
        port = 55121
        while True:
            try:
                server = HTTPServer(('127.0.0.1', port), HTTPRequestHandler)
                break
            except:
                port+=1
        self.server = server
    
    def __run_server(self):
        self.__will_serve = True
        while self.__will_serve:
            self.server.handle_request()

    def __stop_server(self):
        self.__will_serve = False
        time.sleep(POOL_DELAY)

    def get(self):
        # clearing up if have any
        while _ua_list:
            _ua_list.pop()
        
        serverDaemonThread = DaemonThread(self.__run_server)
        serverDaemonThread.start()
        
        if serverDaemonThread.is_alive():
            print('Please go to the following address in the same browser (where you slected the cookies) for configuring User-Agent.')
            print(f'http://127.0.0.1:{self.server.server_port}/')
        else:
            print('Someting went wrong.')
            return None

        for _ in range(int(TIMEOUT/POOL_DELAY)):
            time.sleep(POOL_DELAY)
            if len(_ua_list) > 0:
                self.__stop_server()
                return _ua_list.pop()
        self.__stop_server()
        print('Timeout waiting for User-Agent')
        return None
