from http import server
import socketserver
from urllib import parse
import json
from os import curdir, sep
from scipy.spatial import *
import pandas as pd
'''
Developed with PYTHON 3.7
Basic map generator, intended that it will be possible for it to take the target easting and northing, then return
a suitable map with markers added in, along with their colours
Hopefully possible to extend the functionality to colour entire roads
NOTE that for generation purposes the base data set is used, rather than anything from any predictor, but it will
be easy to substitute the correct data in later
'''
class MapRenderer():
    def __init__(self):
        self.weather = pd.read_csv('met_data_complete.csv', header=[0, 1], index_col=[0, 1])
        self.weather_locations = self.weather.columns
        self.the_tree = cKDTree([thing for thing in self.weather_locations])

    def get_locations(self,easting,northing,radius):
        results = self.the_tree.query_ball_point([(easting, northing)], r=radius)
        return results

'''
Very primitive HTTP server to allow the acceptance of requests and the use of our existing systems to query the 
pre-generated data efficiently and with minimal overhead
Implementation is prrof-of-conept only, is not secure and cannot be extended to be so
Server accepts standard GET parameters as part of the URL, unnecessary to extend to POST requests for this purpose
'''
class MyServer(server.BaseHTTPRequestHandler):

    def serve_test_page(self):
        f = open(curdir + sep + '/test_page.html')
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(f.read().encode('utf-8'))
        f.close()
    # override of the BaseHTTPRequestHandler function to handle GET requests
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


if __name__ == '__main__':
    maprenderer = MapRenderer()
