# WildNav: GNSS-Free drone navigation and localization in the wild

###  Abstract

Considering the accelerated development of Unmanned Aerial Vehicles (UAVs) applications in both industrial and research scenarios, there is an increasing need for localizing these aerial systems in non-urban environments, using GNSS-Free, vision-based methods. Our paper proposes a vision-based localization algorithm that utilizes deep features to compute geographical coordinates of a UAV flying in the wild. The method is based on matching salient features of RGB photographs captured by the drone camera and sections of a pre-built map consisting of georeferenced open-source satellite images. Experimental results prove that vision-based localization has comparable accuracy with traditional GNSS-based methods, which serve as ground truth. Compared to state-of-the-art Visual Odometry (VO) approaches, our solution is designed for long-distance, high-altitude UAV flights.

### Algorithm Overview

![Overview](https://raw.githubusercontent.com/TIERS/wildnav/main/assets/overview/project_overview.png)

<div align=center>
<img src="assets/overview/project_overview.png" width="800px">
<p align="center">Vision-based localization algorithm overview </p>
</div>

<div align=center>
<img src="assets/overview/good_match_examples.png" width="800px">
<p align="center">Examples of successfully matched drones photographs (left) and satellite
images (right) </p>
</div>



## How to run

   1. Clone repo
      ```
      git clone git@github.com:TIERS/wildnav.git
      ```
   3. Install superglue dependencies:
      ```
      git submodule init
      git submodule update
      ```
   3. Install python dependencies
      ```
      pip3 install -r requirements.txt
      ```
   4. Run
      ```
      cd src
      python3 feature_matching_superglue.py
      ```

## Datasets

Photographs used for experimental validation of the algorithm can be found [here](https://utufi.sharepoint.com/:f:/s/msteams_0ed7e9/EsXaX0CKlpxIpOzVnUmn8-sB4yvmsxUohqh1d8nWKD9-BA?e=gPca2s).

<div align=center>
<img src="assets/overview/experiments_flight_area.png" width="800px">
<p align="center">Satellite view of the flight zone (highlighted rectangle). The yellow pin is
located at 60.403091° latitude and 22.461824° longitude </p>
</div>


## Results

<div align=center>

|           	| Total 	| Localized 	| MAE (m) 	|
|:---------:	|:-----:	|:---------:	|:-------:	|
| Dataset 1 	|  124  	|  77 (62%) 	|  15.82  	|
| Dataset 2 	|   78  	|  77 (62%) 	|  26.58  	|

</div>



<div align=center>
<img src="assets/overview/dataset_1_abs_coord.png" width="800px">
<p align="center">Dataset 1 absolute coordinates of localized photographs </p>
</div>

<div align=center>
<img src="assets/overview/dataset_1_error.png" width="800px">
<p align="center">Dataset 1 localization error </p>
</div>

<div align=center>
<img src="assets/overview/dataset_2_abs_coord.png" width="800px">
<p align="center">Dataset 2 absolute coordinates of localized photographs</p>
</div>

<div align=center>
<img src="assets/overview/dataset_2_error.png" width="800px">
<p align="center">Dataset 2 localization error </p>
</div>

<div align=center>
<img src="assets/overview/error_comparison.png" width="800px">
<p align="center">Error comparison </p>
</div>
