from http import server
import socketserver
from urllib import parse
import json

class MyServer(server.BaseHTTPRequestHandler):

    def do_GET(self):
        params = parse.parse_qs(parse.urlsplit(self.path).query)
        if params.get('northing') is not None and params.get('easting') is not None:
            northing = params['northing']
            easting = params['easting']
        print(params)
        # some_function()
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(params).encode('utf-8'))
        self.server.path = self.path



httpd = socketserver.TCPServer(("", 8080), MyServer)
httpd.serve_forever()
