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

NOTE that private browing is sometimes necessary to get reliable behaviour

In Browser:
    to see the map, set 'map' parameter to exist, and set the 'easting' and 'northing' parameters accordingly 
    e.g. http://localhost:8080?map=true&easting=002500&northing=500000
'''


# define enum for use in various functions potentially
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
        icon = {}
        icon['green'] = '{ url: "http://maps.google.com/mapfiles/ms/icons/green-dot.png"}'
        icon['red'] = '{ url: "http://maps.google.com/mapfiles/ms/icons/red-dot.png"}'
        icon['orange'] = '{ url: "http://maps.google.com/mapfiles/ms/icons/orange-dot.png"}'
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
            markers += 'var marker{it} = new google.maps.Marker({{ position: {{ lat: {lat}, lng: {lng} }}, map: map, icon: {icon} }});'.format(lat=coords[1][0],lng=coords[0][0],it=it,icon=icon['green'])
            markers += 'var content{it} = \'<div id="content{it}"> <H1 class="infoTitle"> {name} </H1> <div class="bodyContent"> <p><b>{name}</b></p> </div> </div>\';'.format(it=it,name="Place")
            #markers += 'var content{it} = \'stufff herer \';'.format(it=it)
            markers += 'var infowindow{it} = new google.maps.InfoWindow({{content: content{it}}});'.format(it=it)
            markers += 'marker{it}.addListener("click",function(){{infowindow{it}.open(map,marker{it});}});'.format(it=it)
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
                        <h3>Traffic Points</h3>
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
                           zoom=9,
                           centre_lon=centre[0][0],
                           centre_lat=centre[1][0],
                           markers=markers)
        return google_map

'''
Very primitive HTTP server to allow the acceptance of requests and the use of our existing systems to query the 
pre-generated data efficiently and with minimal overhead
Implementation is proof-of-concept only, is not secure and cannot be extended to be so while using the BaseHTTPRequestHandler
Server accepts standard GET parameters as part of the URL, it is unnecessary to extend to using POST requests for this purpose
'''
class LemServer(server.BaseHTTPRequestHandler):

    def serve_test_page(self):
        f = open(curdir + sep + '/test_page.html')
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(f.read().encode('utf-8'))
        f.close()
    # override of the BaseHTTPRequestHandler function to handle GET requests
    def do_GET(self):
        split = parse.urlsplit(self.path)
        print('path = ', split.path)
        params = parse.parse_qs(split.query)

        if params.get('test') is not None:
            self.serve_test_page()
        elif (split.path == '/map' or split.path == '/map/') and params.get('northing') is not None and params.get('easting') is not None:
            self.serve_map_page(params['easting'], params['northing'])
        elif (split.path == '/map' or split.path == '/map/'):
            if params.get('latitude') is not None and params.get('longitude') is not None:
                centre = convert_bng([float(params['longitude'][0])], [float(params['latitude'][0])])
                self.serve_map_page(centre[0], centre[1], True)
            else:
                self.serve_map_page([888887], [777773], False)
        elif split.path == '/home' or split.path == '/home/':
            self.serve_home_page()
        else:
            self.serve_default_page(params)

    def serve_map_page(self, easting, northing, full):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(curdir + sep + '/map_1.html') as f:
            self.wfile.write(f.read().encode('utf-8'))
        if full:
            self.wfile.write(maprenderer.render_map(easting,northing).encode('utf-8'))
        with open(curdir + sep + '/map_2.html') as g:
            self.wfile.write(g.read().encode('utf-8'))

    def serve_home_page(self):
        f = open(curdir + sep + '/home_page2.html')
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(f.read().encode('utf-8'))
        f.close()

    def serve_default_page(self, params):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(params).encode('utf-8'))
        self.server.path = self.path

print("Starting LemServer on port 8080...")
print("Instantiating MapRenderer...")
maprenderer = MapRenderer()
# Once running, the server is accessed on localhost:8080
# The home page is on /home
print("Launching server on port 8080...")
httpd = socketserver.TCPServer(("", 8080), LemServer)
print("LemServer is operational")
print("running...")
httpd.serve_forever()
print("LemServer shut down")
