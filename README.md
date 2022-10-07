# WildNav Project

GNSS-Free drone navigation and localization in the wild

###  Abstract

Considering the accelerated development of Unmanned Aerial Vehicles (UAVs) applications in both industrial and research scenarios, there is an increasing need for localizing these aerial systems in non-urban environments, using GNSS-Free, vision-based methods. Our paper proposes a vision-based localization algorithm that utilizes deep features to compute geographical coordinates of a UAV flying in the wild. The method is based on matching salient features of RGB photographs captured by the drone camera and sections of a pre-built map consisting of georeferenced open-source satellite images. Experimental results prove that vision-based localization has comparable accuracy with traditional GNSS-based methods, which serve as ground truth. Compared to state-of-the-art Visual Odometry (VO) approaches, our solution is designed for long-distance, high-altitude UAV flights.

### Algorithm Overview

![Overview](https://raw.githubusercontent.com/TIERS/wildnav/main/assets/overview/project_overview.png)

## Vision-based localization

How to run:

   1. Clone repo
      ```
      git@github.com:TIERS/wildnav.git
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

## Datasets

Photographs used for experimental validation of the algorithm can be found [here](https://utufi.sharepoint.com/:f:/s/msteams_0ed7e9/EsXaX0CKlpxIpOzVnUmn8-sB4yvmsxUohqh1d8nWKD9-BA?e=gPca2s).
