from http import server
import socketserver
from urllib import parse
import json
from os import curdir, sep


class MyServer(server.BaseHTTPRequestHandler):

    def serve_test_page(self):
        f = open(curdir + sep + '/test_page.html')
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(f.read().encode('utf-8'))
        f.close()

    def do_GET(self):
        params = parse.parse_qs(parse.urlsplit(self.path).query)
        if params.get('northing') is not None and params.get('easting') is not None:
            northing = params['northing']
            easting = params['easting']
        if params.get('test') is not None:
            self.serve_test_page()
        else:
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(params).encode('utf-8'))
            self.server.path = self.path



httpd = socketserver.TCPServer(("", 8080), MyServer)
httpd.serve_forever()
