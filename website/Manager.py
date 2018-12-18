from http import server
import socketserver
from urllib import parse
import json
from os import curdir, sep
from scipy.spatial import *
import pandas as pd
from convertbng.util import convert_lonlat, convert_bng

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
class MapRenderer():
    def __init__(self):
        self.weather = pd.read_csv('met_data_complete.csv', header=[0, 1], index_col=[0, 1])
        self.weather_locations = self.weather.columns
        self.the_tree = cKDTree([thing for thing in self.weather_locations])

    def get_locations(self,easting,northing,radius):
        results = self.the_tree.query_ball_point([(easting, northing)], r=radius)
        return results
    def render_map(self, easting, northing):
        markers = ''
        for point in self.get_locations(easting, northing, 50000):
            coords = self.weather.loc[easting, northing]
            coords = convert_lonlat([coords[0]],[coords[1]])
            markers += 'var marker = new google.maps.Marker({position: {lat: {lat}, lng: {lng}}, map: map});'.format(lat=coords[1][0],
                                                                                                          lng=coords[0][0])
        google_map = ''''
                <!DOCTYPE html>
                <html>
                    <head>
                        <style>
                            /* Set the size of the div element that contains the map */
                                #map {
                                height: {height};  /* The height is 400 pixels */
                                width: {width};  /* The width is the width of the web page */
                                }
                        </style>
                    </head>
                    <body>
                        <h3>My Google Maps Demo</h3>
                        <!--The div element for the map -->
                        <div id="map"></div>
                        <script>
                    // Initialize and add the map
                    function initMap() {
                          // The map, centered at target location
                          var map = new google.maps.Map(
                          document.getElementById('map'), {zoom: {zoom}, center: {lat: {centre_lat}, lng: {centre_lng}});
                          {markers}
                    }
                        </script>
                            <script async defer
                            src="https://maps.googleapis.com/maps/api/js?callback=initMap">
                        </script>
                    </body>
                </html>
                '''.format(height='80%',
                           width='80%',
                           zoom=4,
                           center_lon=convert_lonlat([easting], [northing])[0][0],
                           center_lat=convert_lonlat([easting], [northing])[1][0],
                           markers=markers)
        return google_map

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
        self.wfile.write(maprenderer.render_map(easting,northing).read().encode('utf-8'))

    def serve_default_page(self, params):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(params).encode('utf-8'))
        self.server.path = self.path
        
maprenderer = MapRenderer()
httpd = socketserver.TCPServer(("", 8080), MyServer)
httpd.serve_forever()

