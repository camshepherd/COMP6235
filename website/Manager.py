from http import server
import socketserver
from urllib import parse
import json
from os import curdir, sep
from scipy.spatial import *
import pandas as pd

class MyServer(server.BaseHTTPRequestHandler):

    def __init__(self):
        self.weather = pd.read_csv('met_data_complete.csv', header=[0, 1], index_col=[0, 1])
        self.weather_locations = self.weather.columns
        self.the_tree = cKDTree([thing for thing in self.weather_locations])
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

    def get_locations(self,easting,northing,radius):
        results = self.the_tree.query_ball_point([(easting, northing)], r=radius)
        return results

    
httpd = socketserver.TCPServer(("", 8080), MyServer)
httpd.serve_forever()
