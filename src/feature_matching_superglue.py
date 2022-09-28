
import numpy as np
import cv2 
import matplotlib.pyplot as plt
import csv
import superglue_utils
import time
import color_mask
import imutils

import haversine as hs
from haversine import Unit

CSV_FLAG = False

class GeoPhotoDrone:
    """Stores a drone photo together with GNSS location and camera rotation parameters
    """
    def __init__(self, filename, photo = 0, latitude = 0, longitude = 0 , altitude = 0 ,gimball_roll = 0, gimball_yaw = 0, gimball_pitch = 0, flight_roll = 0, flight_yaw = 0, flight_pitch = 0):
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

def csv_read_drone_images(filename):
    """Builds a list with drone geo tagged photos by reading a csv file with this format:
    Filename, Top_left_lat,Top_left_lon,Bottom_right_lat,Bottom_right_long
    "big_photo_2.png",60.506787,22.311631,60.501037,22.324467
    """
    geo_list_drone = []
    photo_path = "../photos/query/real_dataset_1/matrice_300_session_2/"
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
    """Builds a list with geo tagged photos by reading a csv file with this format:
    Filename, Top_left_lat,Top_left_lon,Bottom_right_lat,Bottom_right_long
    "big_photo_2.png",60.506787,22.311631,60.501037,22.324467
    """
    geo_list = []
    photo_path = "../photos/map/real_dataset_matrice_2/"
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        print(csv_reader)
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:   
                print(row[0])             
                img = cv2.imread(photo_path + row[0],0)
                geo_photo = GeoPhoto(photo_path + row[0],img,(float(row[1]),float(row[2])), (float(row[3]), float(row[4])))
                geo_list.append(geo_photo)
                line_count += 1

        print(f'Processed {line_count} lines.')
        geo_list.sort() # sort alphabetically by filename to ensure that the feature matcher return the right index of the matched sat image
        return geo_list
    
def csv_write_image_location(photo):
    header = ['Filename', 'Latitude', 'Longitude', 'Calculated_Latitude', 'Calculated_Longitude', 'Latitude_Error', 'Longitude_Error', 'Meters_Error', 'Corrected', 'Matched']
    with open('calculated_coordinates_real_data_2.csv', 'a', encoding='UTF8') as f:
        writer = csv.writer(f)
        # if  not CSV_FLAG:
        #     writer.writerow(header)
        #     CSV_FLAG = True
        
        photo_name = photo.filename.split("/")[-1]
        loc1 = ( photo.latitude, photo.longitude)
        loc2 = ( photo.latitude_calculated, photo.longitude_calculated)
        dist_error =  hs.haversine(loc1,loc2,unit=Unit.METERS)
        lat_error = photo.latitude - photo.latitude_calculated
        lon_error = photo.longitude - photo.longitude_calculated
        line = [photo_name, str(photo.latitude), str(photo.longitude), str(photo.latitude_calculated), str(photo.longitude_calculated), str(lat_error), str(lon_error), str(dist_error), str(drone_image.corrected), str(drone_image.matched), str(drone_image.gimball_yaw + drone_image.flight_yaw - 15)]
        writer.writerow(line)

def calculate_geo_pose(geo_photo, center, features_mean,  shape):
     #use ratio here instead of pixels because image is reshaped in superglue
    query_lat = 0.001
    query_lon = 0.00263
    latitude = geo_photo.top_left_coord[0] + abs( center[1])  * ( geo_photo.bottom_right_coord[0] - geo_photo.top_left_coord[0])
    longitude = geo_photo.top_left_coord[1] + abs(center[0])  * ( geo_photo.bottom_right_coord[1] - geo_photo.top_left_coord[1])
    corrected_lat = latitude -  ((shape[1] / 2  - features_mean[1]) / shape[1]) * query_lat
    corrected_lon = longitude + ((shape[0] / 2  - features_mean[0]) / shape[0])  * query_lon
    
    print("Old coord: ", center, latitude, longitude)
    print("New coord: ", corrected_lat, corrected_lon)
    #input("press enter ")
    return latitude, longitude, corrected_lat, corrected_lon





#Read all the geo tagged images that make up the sattelite map used for reference
geo_images_list = csv_read_sat_map("../photos/map/real_dataset_matrice_2/map.csv")
#drone_images_list = csv_read_drone_images("../photos/query/real_dataset_1/matrice_300_session_1/drone_image_test.csv")
drone_images_list = csv_read_drone_images("../photos/query/real_dataset_1/matrice_300_session_2/matrice_session_2.csv")
print(drone_images_list[7])
#drone_image = cv2.imread("../photos/query/real_dataset_1/matrice_300_session_1/photo_2.JPG", 0)

#write the query image to the map folder
#the query will be matched to every sattelite map image
#drone_image = imutils.rotate(drone_image, 0)
latitude_truth = []
longitude_truth = []
latitude_calculated = []
longitude_calculated = []

print(drone_images_list)
for drone_image in drone_images_list:
    latitude_truth.append(drone_image.latitude)
    longitude_truth.append(drone_image.longitude)
    photo =  cv2.imread(drone_image.filename)
    #photo = imutils.rotate(photo, drone_image.flight_yaw + drone_image.gimball_yaw )
    
    #Try different rotations
    rotations = np.arange(0, 360,10, dtype = int)
    print(rotations)
    #input("Press enter to continue rotations ")
    max_features = 0
    located = False

    rotations = [20]
    center = None

    for rot in rotations:
        
        photo =  cv2.imread(drone_image.filename)
        #photo = imutils.rotate(photo, drone_image.gimball_yaw + drone_image.flight_yaw - 15)
        #photo = imutils.rotate(photo, -300 )
        
        cv2.imwrite("../photos/map/real_dataset_matrice_2/1_query_image.png", photo)
        
        print(drone_image.gimball_yaw + drone_image.flight_yaw)
        #input("Rotation")
        satellite_map_index_new, center_new, located_image_new, features_mean_new, query_image_new, feature_number = superglue_utils.match_image()
        if (feature_number > max_features and center_new[0] < 1 and center_new[1] < 1):
            satellite_map_index = satellite_map_index_new
            center = center_new
            located_image = located_image_new
            features_mean = features_mean_new
            query_image = query_image_new
            max_features = feature_number
            located = True
    photo_name = drone_image.filename.split("/")[-1]
    if center != None and located:        
        current_location = calculate_geo_pose(geo_images_list[satellite_map_index], center, features_mean, query_image.shape )
        #cv2.putText(located_image, str(current_location), org = (10,625),fontFace =  cv2.FONT_HERSHEY_DUPLEX, fontScale = 0.8,  color = (0, 0, 0))
        cv2.imwrite("../results/matrice_session_2/" + photo_name + "_result.png", located_image)
        cv2.imwrite("test_image_loc.png", located_image)
        print("Ground Truth: ", drone_image.latitude, drone_image.longitude)
        print("Located", photo_name,  center, satellite_map_index, features_mean)
        #cv2.circle(query_image, (int(features_mean[0]), int(features_mean[1])), radius = 10, color = (255, 0, 0), thickness = 2)
        # cv2.imshow("query_image", query_image)
        # cv2.waitKey()
        # cv2.destroyAllWindows()
        #input("Press Enter to continue")        
        print("Geographical location: ", current_location)
        drone_image.matched = True
        print(current_location[0])
        print(current_location[1])
        #input("Press Enter to continue...")
        drone_image.latitude_calculated = current_location[0]
        drone_image.longitude_calculated = current_location[1]
        if (abs(drone_image.latitude - current_location[2]) < abs(drone_image.latitude - current_location[0])) and (abs(drone_image.longitude - current_location[3]) < abs(drone_image.longitude - current_location[1])):
            drone_image.latitude_calculated = current_location[2]
            drone_image.longitude_calculated = current_location[3]
            print("corrected latitude and longitude")
            drone_image.corrected = True
        # if (abs(drone_image.longitude - current_location[3]) < abs(drone_image.longitude - current_location[1])):
        #     drone_image.longitude_calculated = current_location[3]
        #     print("corrected longitude")
        #     #input("Press Enter to continue, corrected longitude")
        
        latitude_calculated.append(drone_image.latitude_calculated)
        longitude_calculated.append(drone_image.longitude_calculated)
        #cv2.imshow("Sat map", geo_images_list[satellite_map_index].photo)
        #cv2.waitKey()
        
        #input("Press Enter to continue...")

    else:
        print("NOT MATCHED:", photo_name)
    csv_write_image_location(drone_image)

print(latitude_truth)
print(longitude_truth)
print(latitude_calculated)
print(longitude_calculated)

#csv_write_image_location(drone_images_list)



