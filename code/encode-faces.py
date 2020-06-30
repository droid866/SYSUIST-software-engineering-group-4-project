# coding=utf-8
# import the necessary packages
from imutils import paths
import face_recognition
import argparse
import pickle
import cv2
import os
import numpy as np
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--dataset", type=str,default="dataset",
    help="path to input directory of faces + images")
ap.add_argument("-e", "--encodings",type=str, default="encodings.pickle",
    help="path to serialized db of facial encodings")
ap.add_argument("-d", "--detection-method", type=str, default="hog",
    help="face detection model to use: either `hog` or `cnn`")
args = vars(ap.parse_args())
# grab the paths to the input images in our dataset
print("[INFO] quantifying faces...")
imagePaths = list(paths.list_images(args["dataset"]))
# initialize the list of known encodings and known names
knownEncodings = []
knownNames = []


def cv_imread(file_path):
    cv_img = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)
    return cv_img

# loop over the image paths
for (i, imagePath) in enumerate(imagePaths):
    # extract the person name from the image path
    print("[INFO] processing image {}/{}".format(i + 1,
        len(imagePaths)))
    name = imagePath.split(os.path.sep)[-1].split(".")[0]
    # load the input image and convert it from BGR (OpenCV ordering)
    # to dlib ordering (RGB)
    print(imagePath)
    image = cv_imread(imagePath)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    boxes = face_recognition.face_locations(rgb,model=args["detection_method"])

    w,h=image.shape
    u,r,d,l=boxes[0]
    l = 0 if l - 100 < 0 else l - 100
    r = 0 if r + 100 > w else r + 100
    u = 0 if u - 100 < 0 else u - 100
    d = h if d + 100 > h else d + 100
    image=image[u:d,l:r]



    # compute the facial embedding for the face
    encodings = face_recognition.face_encodings(rgb, boxes)
    # loop over the encodings
    for encoding in encodings:
        # add each encoding + name to our set of known names and
        # encodings
        knownEncodings.append(encoding)
        knownNames.append(name)
# dump the facial encodings + names to disk
print("[INFO] serializing encodings...")
data = {"encodings": knownEncodings, "names": knownNames}
f = open(args["encodings"], "wb")
f.write(pickle.dumps(data))
f.close()