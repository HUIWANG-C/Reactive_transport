import pandas as pd
import numpy as np
import cv2
import os
import re

#******** Automatically detect the file containing 'position_M'*************#
# Path to folder containing images
img_dir = './Pposition_Mass'

# Extract all files that match the pattern Position*.png
image_files = [f for f in os.listdir(img_dir) if f.startswith('Position') and f.endswith('.png')]

# Use regex to extract time values from filenames
def extract_time(filename):
    match = re.search(r'Position([0-9\.]+)\.png', filename)
    return float(match.group(1)) if match else None

# Build a list of (time, filename) tuples
time_file_pairs = [(extract_time(f), f) for f in image_files]
time_file_pairs = [pair for pair in time_file_pairs if pair[0] is not None]

# Sort by time
time_file_pairs.sort(key=lambda x: x[0])

# Extract the sorted times and filenames
Time = [t for t, f in time_file_pairs]
Filenames = [f for t, f in time_file_pairs]

#******************* Read images ***********************************************#
output_file = os.path.join('./Pposition_Mass', 'video.mp4')

# Define your desired video resolution
#desired_width = 1187
#desired_height = 729
desired_width = 814
desired_height = 500
size = (desired_width, desired_height)

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video = cv2.VideoWriter(filename=output_file, fourcc=fourcc, fps=32, frameSize=size, isColor=True)

#******************* Create video ***********************************************#
step = 7  # Use every 3rd frame
for i in range(0, len(Filenames), step):
    filename = Filenames[i]
    T = Time[i]  # Corresponding time

    path = os.path.join('./Pposition_Mass', filename)
    img = cv2.imread(path)
    if img is None:
        print(f"Error reading image at {path}")
        continue

    resized_img = cv2.resize(img, size)
    font = cv2.FONT_HERSHEY_SIMPLEX
    position = (20, int(desired_height * 0.96))
    cv2.putText(resized_img, f"{round(T, 5)}", position, font, 0.5, (0, 0, 0), 1)

    video.write(resized_img)
    print(f"read image at {filename}")

video.release()
print(f'Video saved to: {output_file}')

