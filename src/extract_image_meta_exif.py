import subprocess
import re
import os

############################################################################################################
# Script that reads the EXIF data from the drone images and extracts the GNSS coordinates to a csv file
# You might have to modify the scripts to match the EXIF metadata of your drone photos 
# Use https://www.metadata2go.com/ to easily check the metadata of your images
############################################################################################################

csv_filename = 'photo_metadata.csv' # csv file with drone image metadata containing GNSS location
photo_folder = '../assets/query/' # folder with drone images
 
csv_filename = photo_folder + csv_filename

def convert_gnss_coord(lat_or_lon):
    """
    Convert GNSS coordinate to decimal degrees instead of minutes and seconds
    """
    deg, deg_string, minutes,discard_1,  seconds, discard_2, direction =  re.split('[\s°\'"]', lat_or_lon)
    converted = (float(deg) + float(minutes)/60 + float(seconds)/(60*60)) * (-1 if direction in ['W', 'S'] else 1)
    return str(converted)

def load_images_from_folder(folder):
    images_list = []
    print("Loading images")
    for filename in os.listdir(folder):
        if filename.endswith((".JPG", ".jpg", ".png")):
            images_list.append(filename)

    images_list.sort()
    return images_list

images_list = load_images_from_folder(photo_folder)

f = open(csv_filename, "a")

filesize = os.path.getsize(csv_filename)
if filesize == 0:
    f.write("Filename,Latitude,Longitude,Altitude,Gimball_Roll,Gimball_Yaw,Gimball_Pitch,Flight_Roll,Flight_Yaw,Flight_Pitch")

print("Reading metadata")
for image in images_list:
    infoDict = {} #Creating the dict to get the metadata tags
    exifToolPath = 'exiftool'
    imgPath = photo_folder + image
    process = subprocess.Popen([exifToolPath,imgPath],stdout=subprocess.PIPE, stderr=subprocess.STDOUT,universal_newlines=True) 
    ''' get the tags in dict '''
    for tag in process.stdout:
        line = tag.strip().split(':')
        infoDict[line[0].strip()] = line[-1].strip()
        print(line[0].strip())

    print ("################################################")

    #Default values
    altitude = "NaN"
    gimball_roll = "NaN"
    gimball_yaw = "NaN"
    gimball_pitch = "NaN"
    flight_roll = "NaN"
    flight_yaw = "NaN"
    flight_pitch = "NaN"

    print(infoDict['File Name'])
    if 'File Name' in infoDict:
        filename = infoDict['File Name']
        print(filename)
    if 'GPS Latitude' in infoDict:
        lat = infoDict['GPS Latitude']
    if 'GPS Longitude' in infoDict:
        lon = infoDict['GPS Longitude']
    if 'Relative Altitude' in infoDict:
        altitude = infoDict['Relative Altitude']
    elif 'GPS Altitude' in infoDict:
        altitude = infoDict['GPS Altitude']
        print(infoDict['GPS Altitude'])
        altitude =  re.search(r'\d+', altitude).group() #keep only the number value, discard text
        print(altitude)

    if 'Gimbal Roll Degree' in infoDict:
        gimball_roll = infoDict['Gimbal Roll Degree']
    if 'Gimbal Yaw Degree' in infoDict:
        gimball_yaw = infoDict['Gimbal Yaw Degree']
    if 'Gimbal Pitch Degree' in infoDict:
        gimball_pitch = infoDict['Gimbal Pitch Degree']
    if 'Flight Roll Degree' in infoDict:
        flight_roll = infoDict['Flight Roll Degree']
    if 'Flight Yaw Degree' in infoDict:
        flight_yaw = infoDict['Flight Yaw Degree']
    if 'Flight Pitch Degree' in infoDict:    
        flight_pitch = infoDict['Flight Pitch Degree']

    lat = convert_gnss_coord(lat)
    lon = convert_gnss_coord(lon)

    f.write('\n' + filename + ',' + lat + ',' + lon + ',' + altitude + ',' + gimball_roll + ',' + gimball_yaw + ',' + gimball_pitch + ',' + flight_roll + ','  + flight_yaw + ','+ flight_pitch)

f.close()


