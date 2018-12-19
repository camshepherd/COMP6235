from http import server
import socketserver
from urllib import parse
import json
from os import curdir, sep
from scipy.spatial import *
import pandas as pd
from convertbng.util import convert_lonlat, convert_bng
from enum import Enum

'''
Developed with PYTHON 3.7
The convertbng python library is being used to convert between easting and northing, this is not supported on 
64-bit Windows, but runs fully on Mac and Linux systems
Basic map generator, intended that it will be possible for it to take the target easting and northing, then return
a suitable map with markers added in, along with their colours
Hopefully possible to extend the functionality to colour entire roads
NOTE that for generation purposes the base data set is used, rather than anything from any predictor, but it will
be easy to substitute the correct data in later
'''


# define enum for use in various functions
Conversion = Enum('Conversion', 'bng_to_coords coords_to_bng')


class MapRenderer():
    def __init__(self):
        print("Initialising...")
        self.weather = pd.read_csv('met_data_complete.csv', header=[0, 1], index_col=[0, 1])
        self.weather_locations = self.weather.columns
        self.the_tree = cKDTree([thing for thing in self.weather_locations])
        print("Initialising Renderer...")


    def get_locations(self,easting,northing,radius):
        #print("Easting=", easting[0])
        #print("Northing=", northing[0])
        results = self.the_tree.query_ball_point([(easting[0],northing[0])], r=radius)
        #print("RESULTS:", results[0])
        return results[0]


    def render_map(self, easting, northing):
        markers = ''
        centre = convert_lonlat([int(easting[0])], [int(northing[0])])
        it = 0
        for point in self.get_locations(easting, northing, 50000):
            it += 1
            #print("POINT:", point)
            bng = self.weather_locations[point]
            #print("BNG:", bng)
            coords = convert_lonlat([int(bng[0])],[int(bng[1])])
            #print("COORDS:", coords)
            markers += 'var marker{it} = new google.maps.Marker({{ position: {{ lat: {lat}, lng: {lng} }}, map: map}})\r\n;'.format(lat=coords[1][0],lng=coords[0][0],it=it)
        google_map = '''
                <!DOCTYPE html>
                <html>
                    <head>
                        <style>
                            /* Set the size of the div element that contains the map */
                                #map {{
                                height: {height};  /* The height is 400 pixels */
                                width: {width};  /* The width is the width of the web page */
                                }}
                        </style>
                    </head>
                    <body>
                        <h3>My Google Maps Demo</h3>
                        <!--The div element for the map -->
                        <div id="map"></div>
                        <script>
                    // Initialize and add the map
                    function initMap() {{
                          // The map, centered at target location
                          var map = new google.maps.Map(
                          document.getElementById('map'), {{zoom: {zoom}, center: {{ lat: {centre_lat}, lng: {centre_lon} }} }});
                          {markers}
                    }}
                        </script>
                            <script async defer
                            src="https://maps.googleapis.com/maps/api/js?callback=initMap">
                        </script>
                    </body>
                </html>
                '''.format(height='600px',
                           width='100%',
                           zoom=4,
                           centre_lon=centre[0][0],
                           centre_lat=centre[1][0],
                           markers=markers)
        return google_map

'''
Very primitive HTTP server to allow the acceptance of requests and the use of our existing systems to query the 
pre-generated data efficiently and with minimal overhead
Implementation is proof-of-concept only, is not secure and cannot be extended to be so while using the BaseHTTPRequestHandler
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
        if params.get('test') is not None:
            self.serve_test_page()
        elif params.get('map') is not None and params.get('northing') is not None and params.get('easting') is not None:
            self.serve_map_page(params['easting'], params['northing'])
        else:
            self.serve_default_page(params)

    def serve_map_page(self, easting, northing):

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(maprenderer.render_map(easting,northing).encode('utf-8'))

    def serve_default_page(self, params):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(params).encode('utf-8'))
        self.server.path = self.path
        
maprenderer = MapRenderer()
print("Booting up LemServer...")
httpd = socketserver.TCPServer(("", 8080), MyServer)
print("LemServer running...")
httpd.serve_forever()
print("LemServer STOPPED")
