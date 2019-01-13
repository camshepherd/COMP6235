from http import server
import socketserver
from urllib import parse
import json
from os import curdir, sep
from scipy.spatial import *
import pandas as pd
from convertbng.util import convert_lonlat, convert_bng
from enum import Enum
import datetime
import pickle 


'''
Developed with PYTHON 3.7
The convertbng python library is being used to convert between easting and northing, this is not supported on 
64-bit Windows, but runs fully on Mac and Linux systems
Basic map generator, using easting and northing for all internal calculations
Home is at localhost:8080/home
The map is at /map

NOTE that private browing is sometimes necessary to get reliable behaviour


'''


class MapRenderer():
    def __init__(self):
        print("Initialising...")
        print("Opening DataSet...")
        self.traffic = pd.read_csv('Main_Road_Combined_now.csv')
        print("Opening generic data frame")
        self.generic_frame = pd.read_csv('generic_frame.csv')
        print("Loading prediction model...")
        with open('forest_model_car.pickle','rb') as f:
            self.model = pickle.load(f)
        self.traffic_locations = [(self.traffic.iloc[ref].loc['S Ref E'], self.traffic.iloc[ref].loc['S Ref N']) for ref in self.traffic.index]
        self.the_tree = cKDTree([thing for thing in self.traffic_locations])
        self.category_map = pd.read_csv('category_map.csv')        
        print("Loading Assets...")
        self.icon = {}
        self.icon['green'] = '{ url: "http://maps.google.com/mapfiles/ms/icons/green-dot.png"}'
        self.icon['red'] = '{ url: "http://maps.google.com/mapfiles/ms/icons/red-dot.png"}'
        self.icon['orange'] = '{ url: "http://maps.google.com/mapfiles/ms/icons/orange-dot.png"}'

    def get_locations(self,easting,northing,radius):
        #print("Easting=", easting[0])
        #print("Northing=", northing[0])
        results = self.the_tree.query_ball_point([(easting[0],northing[0])], r=radius)
        #print("RESULTS:", results[0])
        return results[0]

    def get_marker(self, count):
        if count < 350:
            return self.icon['green']
        elif count >= 350 and count < 800:
            return self.icon['orange']
        else:
            return self.icon['red']

    def render_map(self, easting, northing, mintemp, maxtemp, meantemp, rainfall, date):
        date = datetime.datetime.strptime(date,'%Y-%M-%d')

        
        markers = ''
        centre = convert_lonlat([int(easting[0])], [int(northing[0])])
        it = 0
        for point in self.get_locations(easting, northing, 5000):
            it += 1
            #print("POINT:", point)
            bng = self.traffic_locations[point]
            #print("BNG:", bng)
            coords = convert_lonlat([int(bng[0])],[int(bng[1])])
            target = self.traffic.loc[(self.traffic['S Ref E'] == bng[0]) & (self.traffic['S Ref N'] == bng[1])].iloc[0]
            mapping = self.category_map.loc[(self.category_map['S Ref E'] == bng[0]) & (self.category_map['S Ref N'] == bng[1])].iloc[0]
            the_frame = self.generic_frame.copy()
            the_frame[target.loc['Road']] = 1
            the_frame[mapping.loc['RCat']] = 1
            the_frame['year'] = date.year
            the_frame['month'] = date.month
            the_frame['day'] = date.day
            the_frame['max_temp'] = maxtemp
            the_frame['min_temp'] = mintemp
            the_frame['mean_temp'] = meantemp
            the_frame['rainfall'] = rainfall

            prediction = int(self.model.predict(the_frame)[0])
            #print("COORDS:", coords)
            markers += 'var marker{it} = new google.maps.Marker({{ position: {{ lat: {lat}, lng: {lng} }}, map: map, icon: {icon} }});'.format(lat=coords[1][0],lng=coords[0][0],it=it,icon=self.get_marker(prediction))
            markers += 'var content{it} = \'<div id="content{it}"> <H1 class="infoTitle"> {name} </H1> <div class="bodyContent"> <p><b>Car Count: </b> {cars}</p> </div> </div>\';'.format(it=it,name=target.loc['Road'], cars = prediction)
            #markers += 'var content{it} = \'stufff herer \';'.format(it=it)
            markers += 'var infowindow{it} = new google.maps.InfoWindow({{content: content{it}}});'.format(it=it)
            markers += 'marker{it}.addListener("click",function(){{infowindow{it}.open(map,marker{it});}});'.format(it=it)
        google_map = '''
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
                '''.format(height='900px',
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
            self.serve_map_page(params['easting'], params['northing'],True, float(params['tempmin'][0]), float(params['tempmax'][0]), float(params['tempmean'][0]), float(params['rainfall'][0]), params['date'][0])
        elif (split.path == '/map' or split.path == '/map/'):
            if params.get('latitude') is not None and params.get('longitude') is not None:
                centre = convert_bng([float(params['longitude'][0])], [float(params['latitude'][0])])
                self.serve_map_page(centre[0], centre[1], True, float(params['tempmin'][0]), float(params['tempmax'][0]), float(params['tempmean'][0]), float(params['rainfall'][0]), params['date'][0])
            else:
                self.serve_map_page([888887], [777773], False, 0,0,0,0,'')
        elif split.path == '/home' or split.path == '/home/':
            self.serve_home_page()
        else:
            self.serve_default_page(params)

    def serve_map_page(self, easting, northing, full, tempmin, tempmax, tempmean, rainfall, date):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(curdir + sep + '/map_1.html') as f:
            self.wfile.write(f.read().encode('utf-8'))
        if full:
            self.wfile.write(maprenderer.render_map(easting,northing, tempmin, tempmax, tempmean, rainfall, date).encode('utf-8'))
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
