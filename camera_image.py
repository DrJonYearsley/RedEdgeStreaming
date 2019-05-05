# -*- coding: utf-8 -*-
import pandas as pd
from PIL import Image, ImageMath, ImageStat
import numpy as np
import requests
import logging    # Used to make streaming silent
import io
import json
from itertools import compress

import matplotlib.pyplot as plt

# Streams an image and calculate live stats from the image

# Bands 1-5 correspond to the following names
bands = ['blue','green','red','nir','rededge']
save_bands = [True, True, True, True, False]
xOffset = [0, 0, 0, 0, 0]
yOffset = [0, 0, 0, 0, 0]

host = "http://192.168.1.83"



# Calculate the decimal equivalent of the save_codes
# This wil be used for image capture
save_code = 0
for i in range(0,len(bands)):
    save_code += 2**i * save_bands[i]

# Define parameters for camera configuration (this is permanently stored)
config_payload = {'streaming_enable' : False,
                  'timer_period' : 1.0,
                  'auto_cap_mode' : 'disabled',
                  'enabled_bands_raw' : 0,          # This doesn't affect RAM stored previews
                  'enabled_bands_jpeg' : save_code  # This doesn't affect RAM stored previews
}

c = requests.post(host + '/config', data=config_payload)
print(c.text)

# Get camera software version
v = requests.get(host + '/version')
print(v.text)

# Define arguments to control image capture
payload = {'preview' : False,  # This doesn't seem to affect the downloaded image
           'block' : True,
           'store_capture' : False,
           'cache_jpeg' : save_code,
           'cache_raw' : 0}

# Tell the camera to capture data and save in its RAM
r = requests.get(host + '/capture', params=payload, stream=True)

nFile = sum(save_bands)
bandNames = list(compress(bands, save_bands))

# Download images from the camera's RAM to a file as a jpeg
# This works and produces an image that is 215kBytes
npim = np.empty((500,500,nFile))
for i in range(0,nFile):
    #    file = list(r.json()['jpeg_cache_path'].values())[i]
    file = list(r.json()['jpeg_cache_path'].values())[i]
    rf = requests.get(host + file, stream=True)
    outfile = 'rededge_{0}.jpg'.format(bands[i])
    
    with open(outfile, 'wb') as f:
        for chunk in rf.iter_content(10240):
            f.write(chunk)



    
#    # Read byte stream and display image
#    #images.append(Image.open(io.BytesIO(rf.content)))
#    tmp = Image.open(io.BytesIO(rf.content))
#    filename = 'image_raw_{}.bmp'.format(bandNames[i])
#    tmp.save(filename)




# Read files
red = Image.open('rededge_red.jpg')
green = Image.open('rededge_green.jpg')
blue = Image.open('rededge_blue.jpg')
nir = Image.open('rededge_nir.jpg')



# Resize image
width,height = red.size   # Find size of image

# Offsets, order is blue, green, red, nir
# These are good offsets for 2m away
xOffset = [32,10,34,45]   # +ve moves image to right
yOffset = [0,8,32,25]    # +ve moves image down
base = [200,200]

red_crop = red.crop((base[0]-xOffset[2],
                     base[1]-yOffset[2],
                     width-xOffset[2],
                     height-yOffset[2]))

green_crop = green.crop((base[0]-xOffset[1],
                         base[1]-yOffset[1],
                         width-xOffset[1],
                         height-yOffset[1]))

blue_crop = blue.crop((base[0]-xOffset[0],
                       base[1]-yOffset[0],
                       width-xOffset[0],
                       height-yOffset[0]))

nir_crop = nir.crop((base[0]-xOffset[3],
                        base[1]-yOffset[3],
                        width-xOffset[3],
                        height-yOffset[3]))
                 

# Check alignment by creating an RGB image
rgb = Image.merge('RGB',(red_crop,green_crop,blue_crop))
rgb.show()
 

# Normalise red and nir
red_np = np.asarray(red_crop).astype(float)
nir_np = np.asarray(nir_crop).astype(float)

# Calculate the NDVI
ndvi = (nir_np - red_np) / (nir_np+red_np)

# Display image
tmp = Image.fromarray(ndvi*255)
tmp.show()


plt.imshow(ndvi)
plt.show()

# Make ndvi into a pandas dataframe

ndvi_flat = ndvi.flatten(order='F')
shape = ndvi.shape
x,y = np.unravel_index(np.arange(shape[0]*shape[1]), shape)


ndvi_pd = pd.DataFrame([('x', x),('y',y),('pixel',ndvi_flat)])

# Plot
