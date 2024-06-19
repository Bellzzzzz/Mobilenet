# -*- coding: utf-8 -*-
"""Loading_pre_trained_model_CPU_movie.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/10TID_XCETI5i2S0Hi8CDJW4Y4YRzymxq
"""

!pip install tensorflow

import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile

from collections import defaultdict
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image

if tf.__version__ < '1.14.0':
  raise ImportError('Please upgrade your tensorflow installation to v1.4.* or later!')

from PIL import Image, ImageDraw
import cv2

!pip install tensorflow-object-detection-api

from object_detection.utils import label_map_util

from object_detection.utils import visualization_utils as vis_util

!wget http://download.tensorflow.org/models/object_detection/ssd_mobilenet_v2_coco_2018_03_29.tar.gz

!tar -xvf ssd_mobilenet_v2_coco_2018_03_29.tar.gz

# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_CKPT = 'ssd_mobilenet_v2_coco_2018_03_29/frozen_inference_graph.pb'  # change this path

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = './mscoco_label_map.pbtxt'  # change this path

NUM_CLASSES = 90  # change this to the number of objects that you want to detect

!ls

from object_detection.utils import label_map_util
label_map_util.tf = tf.compat.v1
tf.gfile = tf.io.gfile

import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
detection_graph = tf.Graph()
with detection_graph.as_default():
  od_graph_def = tf.GraphDef()
  with tf.io.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
    serialized_graph = fid.read()
    od_graph_def.ParseFromString(serialized_graph)
    tf.import_graph_def(od_graph_def, name='')

label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

from google.colab.patches import cv2_imshow
import cv2
import numpy as np
import time

THRESHOLD = 0.9  # score threshold for detections
font = cv2.FONT_HERSHEY_SIMPLEX

# Load the frozen TensorFlow model

detection_graph = tf.Graph()
with detection_graph.as_default():
    with tf.Session(graph=detection_graph) as sess:
        # Import the model from the frozen graph
        with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as f:
            serialized_graph = f.read()
            detection_graph_def = tf.GraphDef()
            detection_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(detection_graph_def, name='')

        # Open the video file
        cap = cv2.VideoCapture('test1.mp4')

        # Check if the video file is opened correctly
        if not cap.isOpened():
            raise IOError("Cannot open video file.")

        # Set up the TensorFlow detection graph
        image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
        detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
        detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
        detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
        num_detections = detection_graph.get_tensor_by_name('num_detections:0')

        # Create a VideoWriter object to save the output as a video file
        out = cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc(*'MJPG'), 30.0, (640, 480))
        ret, frame = cap.read()
        while cap.isOpened() and frame is not None:
            # Resize the input frame to match the expected size of the detection graph
            frame = cv2.resize(frame, (640, 480))

            # Run the object detection model on the frame
            (boxes, scores, classes, num) = sess.run(
                [detection_boxes, detection_scores, detection_classes, num_detections],
                feed_dict={image_tensor: np.expand_dims(frame, axis=0)})

            # Draw bounding boxes around detected objects with a confidence score > THRESHOLD
            for i, box in enumerate(boxes[0]):
                if scores[0][i] > THRESHOLD:
                    class_id = int(classes[0][i])
                    class_name = category_index[class_id]['name']
                    #print(class_name)
                    frame = cv2.rectangle(frame, (int(box[1]*640),int(box[0]*480)), (int(box[3]*640),int(box[2]*480)), (0,0,255), 2)
                else:
                    continue

            # Show the output using cv2_imshow()
            #cv2_imshow(frame)

            # Save the output frame to the output video file
            out.write(frame)

            # Read the next frame from the video file
            ret, frame = cap.read()
            time.sleep(5)
            # Press esc to exit/stop
     #       c = cv2.waitKey(1)
      #      if c == 27:
       #         break

        # Release the resources and close the windows
        cap.release()
        out.release()
        cv2.destroyAllWindows()

        # A bug in Jupyter Notebook causes it to hangwhen exiting, the lines below are a hack to fix this issue
      #  cv2.waitKey(1)
      #  cv2.waitKey(1)
      #  cv2.waitKey(1)
      #  cv2.waitKey(1)