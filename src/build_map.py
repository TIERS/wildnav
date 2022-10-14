"""Module used for writing csv files"""
import csv
import math
import shutil
import requests



############################################################################################
# Satellite map building script
# Requires access to Google Static Maps API,
#   see https://developers.google.com/maps/documentation/maps-static/overview
# It will not work with current API_KEY, you need to get your own
############################################################################################

# Path to the folder where the map will be saved
MAP_PATH = "../assets/maps/map_2/"
class FlightZone:
    """A rectangle shaped flight area defined by 2 points (latitudes and longitudes)"""
    def __init__(self, top_left_lat, top_left_lon,\
         bottom_right_lat, bottom_right_lon, filename = "default"):
        self.filename = filename
        self.top_left_lat = top_left_lat
        self.top_left_lon = top_left_lon
        self.bottom_right_lat = bottom_right_lat
        self.bottom_right_lon = bottom_right_lon

    def __str__(self):
        return f"{self.__class__.__name__}; \n{self.top_left_lat}: %f \nt{self.top_left_lon}: \
            \n{self.bottom_right_lat}: %f \n{self.bottom_right_lon} %f" 
class PatchSize:
    """Size of a map patch in decimal latitude and longitude"""
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    def __str__(self):
        return f"{self.__class__.__name__}; \n{self.lat}: %f \n{self.lon}"

def csv_write_image_location():
    """Writes a csv file with the geographical location of the downloaded satellite images"""
    header = ["Filename, Top_left_lat,Top_left_lon,Bottom_right_lat,Bottom_right_long"]
    file_path = MAP_PATH + 'map.csv'
    with open(file_path, 'w', encoding='UTF8') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        for photo in photo_list:
            line = [photo.filename, str(photo.top_left_lat), str(photo.top_left_lon), \
                   str(photo.bottom_right_lat), str(photo.bottom_right_lon)]
            writer.writerow(line)

# These 2 variables determine the number of images that form the map

#define as a pair of coordinates determining a rectangle in which the satellite photos will be taken
flight_zone = FlightZone(60.408615, 22.460445, 60.400855, 22.471289)

#define as height (latitude) and width (longitude) of the patch to be taken
patch_size = PatchSize(0.001676, 0.00341)

# Number of satellite patches needed to build the map
width = math.floor((flight_zone.bottom_right_lon -  flight_zone.top_left_lon) / patch_size.lon)
height = math.floor((flight_zone.top_left_lat - flight_zone.bottom_right_lat) / patch_size.lat)

total = width * height
print(f"The script will download : {total} images. Do you want to continue? [Y/N]")
answer = input()

while answer not in ('Y', 'N', 'y', 'n'):
    print("Please answer with Y or N")
    answer = input()

if answer in ('Y', 'y'):
    print("Downloading images...")
elif answer in ('N', 'n'):
    print("Exiting...")
    exit(1)

current_center = PatchSize(flight_zone.top_left_lat - patch_size.lat / 2, \
     flight_zone.top_left_lon + patch_size.lon / 2)
current_top_left = PatchSize(flight_zone.top_left_lat, flight_zone.top_left_lon)
current_bottom_right = PatchSize(current_top_left.lat - patch_size.lat, \
     current_top_left.lon + patch_size.lon)

center = str(current_center.lat) + "," + str(current_center.lon)
zoom = "18" # optimized for the perspective of a wide angle camera at 120 m altitude
size = "640x640"  # maximum allowed size
maptype = "satellite"
scale = "2" # maximum allowed scale
#restricted by IP address, so you will have to generate your own
API_KEY = "AIzaSyAclBCbWo0rwQIaezGcXM6X3S_Otv-hHOQ"

URL = "https://maps.googleapis.com/maps/api/staticmap?" # base URL for the Google Maps API

#defining a params dict for the parameters to be sent to the API
PARAMS = {'center':center,
          'zoom':zoom,
          'size':size,
          'scale':scale,
          'maptype':maptype,
          'key':API_KEY
        }

photo_list = [] # list of all the photos that will be downloaded
index = 0 # index of the current image

# build map by downloading and stitching together satellite images
for i in range(0, height):
    for j in range(0, width):
        photo_name = 'sat_patch' + '_' + f"{index:04d}"+ '.png'

        #send GET request to the API which returns a satellite image upon success
        r = requests.get(url = URL, params = PARAMS, stream=True, timeout=10)


        # if request successful, write image to file
        if r.status_code == 200:
            with open(MAP_PATH + photo_name, 'wb') as out_file:
                shutil.copyfileobj(r.raw, out_file)
                print("image "+ str(index) + " downloaded")
        else:
            print("Error " + r.status_code + " downloading image " + str(index))
        
        current_patch = FlightZone(current_top_left.lat, current_top_left.lon, \
             current_bottom_right.lat, current_bottom_right.lon, photo_name)
        photo_list.append(current_patch)
        index += 1
        current_center.lon = current_center.lon + patch_size.lon
        current_top_left.lon += patch_size.lon
        current_bottom_right.lon += patch_size.lon
        PARAMS['center'] = str(current_center.lat) + "," + str(current_center.lon)
    current_top_left.lat -= patch_size.lat
    current_top_left.lon = flight_zone.top_left_lon
    current_bottom_right.lat -= patch_size.lat
    current_bottom_right.lon = flight_zone.top_left_lon + patch_size.lon
    current_center.lat = current_center.lat - patch_size.lat
    current_center.lon = flight_zone.top_left_lon + patch_size.lon / 2
    PARAMS['center'] = str(current_center.lat) + "," + str(current_center.lon)

print("Map images downloaded, writing csv file")
csv_write_image_location()
print("Map built successfully, check the map folder: " + MAP_PATH)
