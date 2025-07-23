"""
This module contains some functions for pre-processing and post-processing the .dat data generated from PTOF simulations
"""

import numpy as np
import pandas as pd
import os
import re

#******** Automatically detect the file containing 'Keyword' and ending with '.dat'*************#
def detect_file_path(caseDirectory, keyword):
    '''
        func: find and return the path to the first .dat file in `caseDirectory` containing `keyword` in the filename.
        caseDirectory: case folder path
        keyword: the ketword contained in the file name
        return: full path of the file
    '''
    for filename in os.listdir(caseDirectory):                  #loop all the file name
        if keyword in filename and filename.endswith('.dat'):   #check keyword
            file_path = os.path.join(caseDirectory, filename)   #get file path
            #print(f"Using file: {file_path}")
            return file_path                                    #return file path
    print(f"No file found with '{keyword}' in the name.")    
    exit() 

#******** Find the breakthrough time of a case *************#
def breakthrough_time(caseDirectory):
    '''
        func: find the breakthrough of the case from the .dat file containning 'Data_absorption_time_M'
              this function needs to use the previous "detect_file_path" function 
        caseDirectory: case folder path
        return: the breakthrough time
    '''
    #first detect the path of 'Data_absorption_time_M...'
    keyword="Data_absorption_time_M"
    file_path=detect_file_path(caseDirectory, keyword)           #get the file path  
    
    #then read the file and get breakthrough time
    pd.set_option('display.unicode.east_asian_width', True) #solve the problem of out of order
    df = pd.read_table(file_path, sep=r'\s+')  # read data file, names=('Time','Tag','Mass','Patch')
    #print(df.head())       #output the first 5 line
    Time=np.asarray(df['Time'])
    Mass=np.asarray(df['Mass'])
    # Sort outlet data by Time
    sorted_indices = np.argsort(Time)    #returns the indices of the sorted array
    Time_sorted = Time[sorted_indices]   #new time array sorted
    Mass_sorted = Mass[sorted_indices]   #new time array sorted
    breakthrough_time = Time_sorted[0]
    #print(f"Breakthrough time: t= {breakthrough_time}")
    return breakthrough_time

#******** Read Mass file, convert column data into arrarys*************#
def read_Mass_file(file_path, BTtime):
    '''
        func: read the Mass file, return arrays of each column, and arrays of data before breakthrough 
        file_path: the full path of the file
        BTtime: the breakthrough time of the case
        retrun: arrays of time_full, mass_full, time_BT, mass_BT
    '''
    pd.set_option('display.unicode.east_asian_width', True) #solve the problem of out of order
    df = pd.read_table(file_path, sep=r'\s+')  # read data file, names=('Time','Mass') 
    #print(df.head())       #output the first 5 line
    time_full=np.asarray(df['Time'])    # we can also use: time_full = df['Time'].to_numpy() in pandas
    mass_full=np.asarray(df['Mass'])

    df_filtered=df[df['Time'] < BTtime]   #filter the data before breakthrough 
    time_BT=np.asarray(df_filtered['Time'])
    mass_BT=np.asarray(df_filtered['Mass'])
    return time_full, mass_full, time_BT, mass_BT

#******** Generate videos *************#
'''
We define some functions to generate videos using images.
- extract time value from image name
- generate video
- display video
'''


import cv2

def extract_time(filename):
    '''
        func: extract the time from the file 
        file_path: the full path of the file
        BTtime: the breakthrough time of the case
        retrun: arrays of time_full, mass_full, time_BT, mass_BT    
    '''
    match = re.search(r'Position([0-9\.]+)\.png', filename)
    return float(match.group(1)) if match else None

def generate_video(img_dir, output_name='video.mp4', fps=20, step=1, size=(800, 600)):
    image_files = [f for f in os.listdir(img_dir) if f.startswith('Position') and f.endswith('.png')]
    time_file_pairs = [(extract_time(f), f) for f in image_files if extract_time(f) is not None]
    time_file_pairs.sort(key=lambda x: x[0])
    
    output_path = os.path.join(img_dir, output_name)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(output_path, fourcc, fps, size)

    for t, f in time_file_pairs[::step]:
        img_path = os.path.join(img_dir, f)
        img = cv2.imread(img_path)
        if img is None:
            print(f"❌ Error reading: {img_path}")
            continue
        resized = cv2.resize(img, size)
        cv2.putText(resized, f"t = {t:.3f}", (20, size[1] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
        video.write(resized)

    video.release()
    print(f"✅ Saved: {output_path}")
    return output_path

def show_videos_grid(video_paths, labels=None, columns=2, width=400):
    html = "<table><tr>"
    for i, path in enumerate(video_paths):
        if i > 0 and i % columns == 0:
            html += "</tr><tr>"
        label = labels[i] if labels else os.path.basename(path)
        html += f"<td><b>{label}</b><br><video width={width} controls><source src='{path}' type='video/mp4'></video></td>"
    html += "</tr></table>"
    display(HTML(html))



    