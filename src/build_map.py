import requests
import shutil

class FlightZone:
    """A rectangle shaped flight area defined by 2 points (latitudes and longitudes)"""
    def __init__(self,top_left_lat, top_left_lon, bottom_right_lat, bottom_right_lon):
        self.top_left_lat = top_left_lat
        self.top_left_lon = top_left_lon
        self.bottom_right_lat = bottom_right_lat
        self.bottom_right_lon = bottom_right_lon

    def __str__(self):
        return "%s; \ntop_left_lat: %f \ntop_left_lon: %f \nbottom_right_lat: %f \nbottom_right_lon: %f" % (self.__class__.__name__, self.top_left_lat, self.top_left_lon, self.bottom_right_lat, self.bottom_right_lon)

class PatchSize:
    """Size of a map patch in decimal latitude and longitude"""
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    def __str__(self):
        return "%s; \nlat: %f \nlon: %f" % (self.__class__.__name__, self.lat, self.lon)

# These 2 variables determine the number of images that form the map
flight_zone = FlightZone(60.408615, 22.460445, 60.400855, 22.471289) #define as a pair of coordinates determining a rectangle in which the satellite photos will be taken
patch_size = PatchSize(0.001676, 0.00341) #define as height (latitude) and width (longitude) of the patch to be taken




center = "60.403066,22.462214"
zoom = "18" # optimized for the perspective of a wide angle camera at 120 m altitude
size = "640x640"  # maximum allowed size
maptype = "satellite"
scale = "2" # maximum allowed scale
key = "AIzaSyAclBCbWo0rwQIaezGcXM6X3S_Otv-hHOQ" #restricted by IP address, so it will not work if you are not in the lab

#URL = "https://maps.googleapis.com/maps/api/staticmap?center=60.403066,22.462214&zoom=18&size=640x640&scale=2&maptype=satellite&key=AIzaSyD3uC7jYBv2UDe6NO5bx8iWJ2cHIjdPSO0"

OLD_URL =  "https://maps.googleapis.com/maps/api/staticmap?center=60.403066,22.462214&zoom=18&size=640x640&scale=2&maptype=satellite&key=AIzaSyD3uC7jYBv2UDe6NO5bx8iWJ2cHIjdPSO0" 
URL = "https://maps.googleapis.com/maps/api/staticmap?"
  
#defining a params dict for the parameters to be sent to the API

PARAMS = {'center':center,
          'zoom':zoom,
          'size':size,
          'scale':scale,
          'maptype':maptype,
          'key':key
        }
          
  
# sending get request and saving the response as response object

r = requests.get(url = URL, params = PARAMS, stream=True)


# if request successful, write image to file
if r.status_code == 200:
    with open('img.png', 'wb') as out_file:
        shutil.copyfileobj(r.raw, out_file)
        print("image downloaded")
else:
    print("Error ", r.status_code)
