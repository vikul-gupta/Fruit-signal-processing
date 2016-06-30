# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import subprocess
import sys
import matplotlib.pyplot as plt
import argparse

# read command line args
parser = argparse.ArgumentParser()
parser.add_argument('--fruit', choices = ['raspberry', 'grape', 'basil', 'r', 'g', 'b'],
                    required = True, help = 'Type of fruit: raspberry, grape, or basil.')
parser.add_argument('--variety', required = True, help = 'Variety of fruit.')

# create and name files
args_list = sys.argv[1:]
tsf = str(int(time.time()))
name_dict = vars(parser.parse_args(args_list))
name = name_dict['fruit'] + '_' + name_dict['variety'] + '_' + tsf
fname = 'f' + name + '.jpg'
sname = 's' + name + '.png'
dname = 'd' + name + '.dat'

# initialize the camera and grab a reference
camera = PiCamera()
camera.exposure_mode = 'verylong'
rawCapture = PiRGBArray(camera)

# allow the camera to warmup
time.sleep(0.1)

# grab an image from the camera
camera.capture(rawCapture, format = 'bgr')
image = rawCapture.array
img = np.asarray(image)
w = 1
h = 0.2
print (img)
"""
# save image to a file
i = int(sys.argv[len(sys.argv - 1)])
f = open('spectra' + str(i), 'w')
f.write(str(image))
"""
# get spectral data from image array
maxl = image.sum(axis = 2).argmax(axis = 0)
hist = np.histogram(maxl, bins = 100)
setInLine = int(hist[1][hist[0].argmax()])

numl = 10
rarray = np.zeros((w, numl))
garray = np.zeros((w, numl))
barray = np.zeros((w, numl))

startl = setInLine - numl/2
for i in range(w):
    for j in range(numl):
        b,g,r = image[startl + numl][i]
        rarray[w-1-i,j] = r/255.
        garray[w-1-i,j] = g/255.
        barray[w-1-i,j] = b/255.

rl=rarray.mean(axis = 1)
gl=garray.mean(axis = 1)
bl=barray.mean(axis = 1)

fullsp = (rl + gl + bl)/3.

# distorsion: correct = b*(dist - f)
# b = 0.88
# f = 239.535

plt.figure(figsize = (14, 6))
xval = [0.88 * (dist - 237.) for dist in range(rl.shape[0])]
plt.plot(xval[600:1100], rl[600:1100], 'r');
plt.plot(xval[600:1100], gl[600:1100], 'g');
plt.plot(xval[600:1100], bl[600:1100], 'b');
plt.plot(xval[600:1100], fullsp[600:1100], color='black', lw=2);
#plt.savefig('s1465144523.png', dpi = 300, figsize = (14,6))
plt.savefig(sname, dpi = 600)

savedata = np.zeros((len(rl), 4))
savedata[:,0] = rl
savedata[:,1] = gl
savedata[:,2] = bl
savedata[:,3] = fullsp

np.savetxt(dname, savedata, fmt = '%10.5f', delimiter = ',')
