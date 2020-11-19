# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# add_rgb_from_gtiff_from_point_cloud_dir.py
#
# Created by: Rose Phillips
# Created on: 17/11/2020
#
# Description:
# Adds RBG band from user inputted geotiff imagery into LAS or LAZ file.
# ---------------------------------------------------------------------------
from datetime import datetime
import os
from subprocess import PIPE, Popen

imagery_file_dir = input("Enter Imagery Folder Path -> ").replace("\\", "/")
pointcloud_dir = input("Enter Point Cloud Folder Path -> ").replace("\\", "/")
pointcloud_output_dir = os.path.join(pointcloud_dir, "Colourized").replace("\\", "/")

print (f"Script Started: {datetime.now()}")

def create_output_dir(output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)   

def absolute_file_paths_geotiff(directory):
    path = os.path.abspath(directory)
    return [(entry.path).replace("\\", "/") for entry in os.scandir(path) if entry.is_file() and os.path.splitext(entry)[1] == ".tif"]

def absolute_file_paths_las_laz(directory):
    path = os.path.abspath(directory)
    return [(entry.path).replace("\\", "/") for entry in os.scandir(path) if entry.is_file() and os.path.splitext(entry)[1] == ".laz" or os.path.splitext(entry)[1] == ".las"]

def match_image_to_point_clouds(imagery_files, pointcloud_files, pointcloud_dir, pointcloud_output_dir):

    colour_dict = {}

    for file_ in imagery_files:
        pointcloud_name = os.path.basename(os.path.splitext(file_)[0])
        
        # Auckland North Specific File Naming Convention - modify here
        pointcloud_name = ("CL3_" + pointcloud_name[0:4] + "_2016_1000_" + pointcloud_name[-4:] + ".laz").replace("\\", "/")
        point_cloud_abspath = os.path.join(pointcloud_dir, pointcloud_name).replace("\\", "/")
        
        # Write your own specific one here
        print (point_cloud_abspath)

        # if this point cloud file exists then add to dictionary, if not omit
        if os.path.isfile(point_cloud_abspath):

            coloured_point_cloud_file = os.path.join(pointcloud_output_dir, os.path.splitext(pointcloud_name)[0] + "_coloured.laz").replace("\\", "/")

            if point_cloud_abspath not in colour_dict.keys():
                colour_dict[file_] = [point_cloud_abspath, coloured_point_cloud_file]
            else:
                colour_dict[file_].append(point_cloud_abspath, coloured_point_cloud_file)
                print (f"More than one image for this point cloud file {imagery_name}")
    
    return colour_dict

def add_rgb_to_pointclouds(imagery_file_dir, pointcloud_input_dir, pointcloud_output_dir, colour_dict):

    for key in colour_dict:

        if os.path.splitext(key)[1] == ".las":

            pdal_command = f"pdal pipeline C:/a/pdal_add_rgb.json --readers.las.filename={key} --writers.las.filename={colour_dict[key][1]} --filters.colorization.raster={colour_dict[key][0]}"
            pdal_command = pdal_command.split()

            try:
                sp = Popen(pdal_command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                sp_pipe = sp.communicate()
                sp_sterr = sp_pipe[1].decode("utf-8")

                # if any error messages from pdal subprocess, return error message and break script
                if len(sp_sterr) > 0:
                    print (f"error on {key}")
                    print (sp_sterr)
                    break

            except Exception as error:
                print (f"Exception Error on {key}")
                print (error)
                break

        elif os.path.splitext(key)[1] == ".laz":
            
            pdal_command = f"pdal pipeline C:/a/pdal_add_rgb.json --readers.las.filename={key} --writers.las.filename={colour_dict[key][1]} --filters.colorization.raster={colour_dict[key][0]}"
            pdal_command = pdal_command.split()

            try:
                sp = Popen(pdal_command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                sp_pipe = sp.communicate()
                sp_sterr = sp_pipe[1].decode("utf-8")

                # if any error messages from pdal subprocess, return error message and break script
                if len(sp_sterr) > 0:
                    print (f"error on {key}")
                    print (sp_sterr)
                    break

            except Exception as error:
                print (f"Exception Error on {key}")
                print (error)
                break

create_output_dir(pointcloud_output_dir)
imagery_files = absolute_file_paths_geotiff(imagery_file_dir)
pointcloud_files = absolute_file_paths_las_laz(pointcloud_dir)
colour_dict = match_image_to_point_clouds(imagery_files, pointcloud_files, pointcloud_dir, pointcloud_output_dir)
add_rgb_to_pointclouds(imagery_file_dir, pointcloud_dir, pointcloud_output_dir, colour_dict)

print (f"Script Finished: {datetime.now()}")