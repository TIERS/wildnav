# importing the requests library
from numpy import size
import requests
import shutil

# These 2 varibles determine the number of images that form the map
flight_zone = None #define as a pair of coordinates determining a rectangle in which the satellite photos will be taken
patch_size = None #define as height (latitude) and width (longitude) of the patch to be taken

center = "60.403066,22.462214"
zoom = "18"
size = "640x640"
maptype = "satellite"
scale = "2"
key = "AIzaSyAclBCbWo0rwQIaezGcXM6X3S_Otv-hHOQ"

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
#r = requests.get(url = URL, params = PARAMS)
r = requests.get(url = URL, params = PARAMS, stream=True)


if r.status_code == 200:
    with open('img.png', 'wb') as out_file:
        shutil.copyfileobj(r.raw, out_file)
        print("image downloaded")
else:
    print("Error ", r.status_code)
