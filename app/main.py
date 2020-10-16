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
import tempfile

import json
from flask import Flask, jsonify, Response, request, current_app
from flask_cors import CORS, cross_origin


app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/v1/matisse', methods=['POST'])
@cross_origin()
def create_upload_file(): # fic
    data = request.files['file']
    npimg = np.fromfile(data, np.uint8)
    img = image.imdecode(npimg)

    #resize image we got
    (h, w) = img.shape[:2]
    dim = (500, int(h * (500/float(w))))
    img = gdata.transforms.image.imresize(img, dim[0], dim[1])

    #dupe our image for later!
    oimg = img.copy()

    #run img processing here!
    ctx = mx.cpu(0)

    #transform img!
    img = test_transform(img, ctx)

    #get pretrained model
    model = gluoncv.model_zoo.get_model('psp_resnet50_ade', pretrained=True)

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
    
    #make unique image title
    im = Image.fromarray(newImage, 'RGB')
    tBitmap = tempfile.NamedTemporaryFile(suffix='.bmp').name
    im.save(tBitmap)

    #run our image through autoTrace!
    #change this to work on server!
    #if on macOS:
    #svgString = os.popen("./autotrace.app/Contents/MacOS/autotrace -output-format=svg %s" % (tBitmap)).read()
    svgString = os.popen("autotrace -output-format=svg %s" % (tBitmap)).read()

    print(svgString)

    #repair SVG
    xmldoc = minidom.parseString(svgString)
    tags = xmldoc.getElementsByTagName("svg")
    tags[0].attributes["version"] = "1.0"
    tags[0].attributes["xmlns"] = "http://www.w3.org/2000/svg"

    #return SVG content
    svgString = xmldoc.toxml()
    return jsonify (svg=svgString,)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=80)