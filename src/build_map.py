# importing the requests library
import requests
import shutil
  

URL = "https://maps.googleapis.com/maps/api/staticmap?center=Turku+Finland,NY&zoom=17&size=1920x1080&maptype=satellite&markers=color:blue|label:S|40.702147,-74.015794&markers=color:green|label:G|40.711614,-74.012318&markers=color:red|label:C|40.718217,-73.998284&key=AIzaSyAclBCbWo0rwQIaezGcXM6X3S_Otv-hHOQ"
  
# location given here
#location = "finland turku"
  
# defining a params dict for the parameters to be sent to the API
#PARAMS = {'address':location}
  
# sending get request and saving the response as response object
#r = requests.get(url = URL, params = PARAMS)
r = requests.get(url = URL, stream=True)

with open('img.png', 'wb') as out_file:
    shutil.copyfileobj(r.raw, out_file)
