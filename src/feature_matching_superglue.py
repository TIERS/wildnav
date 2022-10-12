import numpy as np
import cv2
import csv
import superglue_utils

import haversine as hs
from haversine import Unit

############################################################################################################
# Important variables
############################################################################################################

map_filename = "../assets/map/map.csv" #  csv file with the sattelite geo tagged images
drone_photos_filename = "../assets/query/photo_metadata.csv" # csv file with the geo tagged drone images;
                                                             # the geo coordinates are only used to compare
                                                             # the calculated coordinates with the real ones
                                                             # after the feature matching

############################################################################################################
# Class definitios
############################################################################################################
class GeoPhotoDrone:
    """Stores a drone photo together with GNSS location
    and camera rotation parameters
    """
    def __init__(self,filename, photo=0, latitude=0, longitude = 0 ,\
         altitude = 0 ,gimball_roll = 0, gimball_yaw = 0, gimball_pitch = 0, flight_roll = 0, flight_yaw = 0, flight_pitch = 0):
        self.filename = filename
        self.photo = photo
        self.latitude = latitude
        self.longitude = longitude
        self.latitude_calculated = -1
        self.longitude_calculated = -1
        self.altitude = altitude
        self.gimball_roll = gimball_roll
        self.gimball_yaw = gimball_yaw
        self.gimball_pitch = gimball_pitch
        self.flight_roll = flight_roll
        self.flight_yaw = flight_yaw
        self.flight_pitch = flight_pitch
        self.corrected = False
        self.matched = False

    def __str__(self):
        return "%s; \nlatitude: %f \nlongitude: %f \naltitude: %f \ngimball_roll: %f \ngimball_yaw: %f \ngimball_pitch: %f \nflight_roll: %f \nflight_yaw: %f \nflight_pitch: %f" % (self.filename, self.latitude, self.longitude, self.altitude, self.gimball_roll, self.gimball_yaw, self.gimball_pitch, self.flight_roll, self.flight_yaw, self.flight_pitch )
        
class GeoPhoto:
    """Stores a satellite photo together with (latitude, longitude) for top_left and bottom_right_corner
    """
    def __init__(self, filename, photo, geo_top_left, geo_bottom_right):
        self.filename = filename
        self.photo = photo
        self.top_left_coord = geo_top_left
        self.bottom_right_coord = geo_bottom_right

    def __lt__(self, other):
         return self.filename < other.filename

    def __str__(self):
        return "%s; \n\ttop_left_latitude: %f \n\ttop_left_lon: %f \n\tbottom_right_lat: %f \n\tbottom_right_lon %f " % (self.filename, self.top_left_coord[0], self.top_left_coord[1], self.bottom_right_coord[0], self.bottom_right_coord[1])


############################################################################################################
# Functions for data writing and reading csv files
############################################################################################################
def csv_read_drone_images(filename):
    """Builds a list with drone geo tagged photos by reading a csv file with this format:
    Filename, Top_left_lat,Top_left_lon,Bottom_right_lat,Bottom_right_long
    "photo_name.png",60.506787,22.311631,60.501037,22.324467
    """
    geo_list_drone = []
    photo_path = "../assets/query/"
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:                
                #img = cv2.imread(photo_path + row[0],0)
                geo_photo = GeoPhotoDrone(photo_path + row[0], 0, float(row[1]), float(row[2]), float(row[3]), float(row[4]), float(row[5]), float(row[6]), float(row[7]), float(row[8]), float(row[9]))
                geo_list_drone.append(geo_photo)
                line_count += 1

        print(f'Processed {line_count} lines.')
        return geo_list_drone

def csv_read_sat_map(filename):
    """Builds a list with satellite geo tagged photos by reading a csv file with this format:
    Filename, Top_left_lat,Top_left_lon,Bottom_right_lat,Bottom_right_long
    "photo_name.png",60.506787,22.311631,60.501037,22.324467
    """
    geo_list = []
    photo_path = "../assets/map/"
    print("opening: ",filename)
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:            
                img = cv2.imread(photo_path + row[0],0)
                geo_photo = GeoPhoto(photo_path + row[0],img,(float(row[1]),float(row[2])), (float(row[3]), float(row[4])))
                geo_list.append(geo_photo)
                line_count += 1

        print(f'Processed {line_count} lines.')
        geo_list.sort() # sort alphabetically by filename to ensure that the feature matcher return the right index of the matched sat image
        return geo_list
    
def csv_write_image_location(photo):
    header = ['Filename', 'Latitude', 'Longitude', 'Calculated_Latitude', 'Calculated_Longitude', 'Latitude_Error', 'Longitude_Error', 'Meters_Error', 'Corrected', 'Matched']
    with open('../results/calculated_coordinates.csv', 'a', encoding='UTF8') as f:
        writer = csv.writer(f)        
        photo_name = photo.filename.split("/")[-1]
        loc1 = ( photo.latitude, photo.longitude)
        loc2 = ( photo.latitude_calculated, photo.longitude_calculated)
        dist_error =  hs.haversine(loc1,loc2,unit=Unit.METERS)
        lat_error = photo.latitude - photo.latitude_calculated
        lon_error = photo.longitude - photo.longitude_calculated
        line = [photo_name, str(photo.latitude), str(photo.longitude), str(photo.latitude_calculated), str(photo.longitude_calculated), str(lat_error), str(lon_error), str(dist_error), str(drone_image.corrected), str(drone_image.matched), str(drone_image.gimball_yaw + drone_image.flight_yaw - 15)]
        writer.writerow(line)


def calculate_geo_pose(geo_photo, center, features_mean,  shape):
    """
    Calculates the geographical location of the drone image.
    Input: satellite geotagged image, relative pixel center of the drone image, 
    (center with x = 0.5 and y = 0.5 means the located features are in the middle of the sat image)
    pixel coordinatess (horizontal and vertical) of where the features are localted in the sat image, shape of the sat image
    """
    #use ratio here instead of pixels because image is reshaped in superglue    
    latitude = geo_photo.top_left_coord[0] + abs( center[1])  * ( geo_photo.bottom_right_coord[0] - geo_photo.top_left_coord[0])
    longitude = geo_photo.top_left_coord[1] + abs(center[0])  * ( geo_photo.bottom_right_coord[1] - geo_photo.top_left_coord[1])
    
    return latitude, longitude



#######################################
# MAIN
#######################################

#Read all the geo tagged images that make up the sattelite map used for reference

geo_images_list = csv_read_sat_map(map_filename)
drone_images_list = csv_read_drone_images(drone_photos_filename)

#write the query image to the map folder
#the query will be matched to every sattelite map image
latitude_truth = []
longitude_truth = []
latitude_calculated = []
longitude_calculated = []

print(str(len(drone_images_list)) + "drone photos were loaded.")


# Iterate through all the drone images
for drone_image in drone_images_list:
    latitude_truth.append(drone_image.latitude) # ground truth from drone image metadata for later comparison
    longitude_truth.append(drone_image.longitude) # ground truth for later comparison
    photo =  cv2.imread(drone_image.filename) # read the drone image
    

    max_features = 0 # keep track of the best match, more features = better match
    located = False # flag to indicate if the drone image was located in the map
    center = None # center of the drone image in the map


    rotations = [20] # list of rotations to try
                     # keep in mind GNSS metadata could have wrong rotation angle
                     # so we try to match the image with different (manually established) rotations

    # Iterate through all the rotations, in this case only one rotation
    for rot in rotations:
        
        # Write the query photo to the map folder
        cv2.imwrite("../assets/map/1_query_image.png", photo)

        #Call superglue wrapper function to match the query image to the map
        satellite_map_index_new, center_new, located_image_new, features_mean_new, query_image_new, feature_number = superglue_utils.match_image()
        
        # If the drone image was located in the map and the number of features is greater than the previous best match, then update the best match
        # Sometimes the pixel center returned by the perspective transform exceeds 1, discard the resuls in that case
        if (feature_number > max_features and center_new[0] < 1 and center_new[1] < 1):
            satellite_map_index = satellite_map_index_new
            center = center_new
            located_image = located_image_new
            features_mean = features_mean_new
            query_image = query_image_new
            max_features = feature_number
            located = True
    photo_name = drone_image.filename.split("/")[-1]

    # If the drone image was located in the map, calculate the geographical location of the drone image
    if center != None and located:        
        current_location = calculate_geo_pose(geo_images_list[satellite_map_index], center, features_mean, query_image.shape )
        
        # Write the results to the image result file with the best match
        cv2.putText(located_image, "Calculated: " + str(current_location), org = (10,625),fontFace =  cv2.FONT_HERSHEY_DUPLEX, fontScale = 0.8,  color = (0, 0, 0))
        cv2.putText(located_image, "Ground truth: " + str(drone_image.latitude) + ", " + str(drone_image.longitude), org = (10,655),fontFace =  cv2.FONT_HERSHEY_DUPLEX, fontScale = 0.8,  color = (0, 0, 0))
        cv2.imwrite("../results/" + photo_name + "_located.png", located_image)
        
        print("Image " + str(photo_name) + " was successfully located in the map")
        print("Calculated location: ", str(current_location[0:2]))
        print("Ground Truth: ", drone_image.latitude, drone_image.longitude)   
        
        # Save the calculated location for later comparison with the ground truth
        drone_image.matched = True
        drone_image.latitude_calculated = current_location[0]
        drone_image.longitude_calculated = current_location[1]
        
        latitude_calculated.append(drone_image.latitude_calculated)
        longitude_calculated.append(drone_image.longitude_calculated)

    else:
        print("NOT MATCHED:", photo_name)

    # Write the results to the csv file    
    csv_write_image_location(drone_image)

