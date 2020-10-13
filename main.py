import mxnet as mx
from mxnet import image
from mxnet.gluon.data.vision import transforms
import gluoncv
from gluoncv.data.transforms.presets.segmentation import test_transform
from gluoncv import data as gdata

import matplotlib.image as mpimg

from PIL import Image
import numpy as np

import os
from xml.dom import minidom

import sys

#get image
img = image.imread(sys.argv[1])
oimg = img.copy()

#resize image we got
(h, w) = img.shape[:2]
dim = (500, int(h * (500/float(w))))
img = gdata.transforms.image.imresize(img, dim[0], dim[1])


newName = sys.argv[2]

#run img processing here!
ctx = mx.cpu(0)

#transform img!
img = test_transform(img, ctx)

#get pretrained model
model = gluoncv.model_zoo.get_model('psp_resnet101_ade', pretrained=True)

print("got model")


#run predict
output = model.predict(img)
predict = mx.nd.squeeze(mx.nd.argmax(output, 1)).asnumpy()

#color image
newImage = np.zeros((predict.shape[0], predict.shape[1], 3), dtype=np.int8)

data = mx.nd.argmax(output, 1).asnumpy()
ulayers = np.unique(data)

myImage = oimg.asnumpy()

for layer in ulayers:    
    myMask = (data == layer)
    
    # mask out current layer
    y=np.expand_dims(myMask,axis=1)
    newmask=np.concatenate((y,y,y),axis=1)
    newmask=np.moveaxis(newmask[0,:,:,:], 0, -1)
    newRegion = myImage * newmask
    
    #find most common color
    img_temp = newRegion.copy()
    img_temp = img_temp.reshape(-1, 3)
    img_temp = img_temp[np.any(img_temp != [0,0,0], axis=1)]
    unique, counts = np.unique(img_temp, axis=0, return_counts=True)
    
    #make new mask that has that color
    newRegion2 = newRegion.copy()
    newRegion2[:,:,:] = unique[np.argmax(counts)]
    newRegion2 = newRegion2 * newmask
    
    #add that mask to a new image
    newImage += newRegion2
    

im = Image.fromarray(newImage, 'RGB')
im.save('in.bmp')

print("running trace")

os.system("./autotrace.app/Contents/MacOS/autotrace -output-file=%s -output-format=svg in.bmp" % (newName))

xmldoc = minidom.parse(newName)

tags = xmldoc.getElementsByTagName("svg")

tags[0].attributes["version"] = "1.0"
tags[0].attributes["xmlns"] = "http://www.w3.org/2000/svg"

with open(newName, "w") as f:
    xmldoc.writexml(f)