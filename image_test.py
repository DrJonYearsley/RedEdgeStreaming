#Edit the following two variables to match your camera's ethernet IP for "host"
#and the path to your external storage device for "path"
#Please note the formatting, keep the "/" on the end
host = "http://192.168.1.83"
#path = "/Users/jon/Desktop/test_pics"

'''DO NOT edit anything below this line
----------------------------------------------------------------------------------------------
'''

import requests
import json
import io
import pandas as pd
import numpy as np
from PIL import Image


# Bands 1-5 correspond to the following names
bands = ['blue','green','red','nir','rededge']
save_bands = [True, True, True, False, False]

# Calculate the decimal equivalent of the save_codes
# This wil be used for image capture
save_code = 0
for i in range(0,len(bands)):
    save_code += 2**i * save_bands[i]

#cload = {'enabled_bands_raw' : 0,'enabled_bands_jpeg':1}
#c = requests.post(host + 'config',params=cload)

# Define arguments to control image capture
payload = {'preview' : False,
           'block' : True,
           'store_capture' : False,
           'cache_jpeg' : save_code,
           'cache_raw' : 0}

# Tell the camera to capture data and save in its RAM
r = requests.get(host + '/capture', params=payload, stream=True)


nfile = len(r.json()['jpeg_cache_path']) # Number of saved images

# # Download images from the camera's RAM and save to a file
# for i in range(0,nfile):
#     file = list(r.json()['jpeg_cache_path'].values())[i]
#     rf = requests.get(host + file, stream=True)
#     outfile = path + '/test_{0}.jpg'.format(bands[i])
#       
#     with open(outfile, 'wb') as f:
#         for chunk in rf.iter_content(10240):
#             f.write(chunk)

# Download images from the camera's RAM as a json object
images = []
for i in range(0,nfile):
    file = list(r.json()['jpeg_cache_path'].values())[i]
    rf = requests.get(host + file, stream=False)
      
    # Read byte stream and display image  
    images.append(Image.open(io.BytesIO(rf.content)))


images[1].show()
    
# convert image into np array
npim = np.empty((960,1280,3))
npim[:,:,0] = np.asarray(images[2])
npim[:,:,1] = np.asarray(images[1])
npim[:,:,2] = np.asarray(images[0])
    
