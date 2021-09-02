import os
import shutil
import cv2

import tensorflow as tf


# Set up directories
# SCRIPT_DIR = os.getcwd()
CALIB_DIR = os.path.join(os.getcwd(), '_calib_dir')
TESTIMG_DIR = os.path.join(os.getcwd(), '_mnist_test')
# IMAGE_LIST_FILE = 'calib_list.txt'

# Create outpu directory
if (os.path.exists(CALIB_DIR)):
    shutil.rmtree(CALIB_DIR)
os.mkdir(CALIB_DIR)

if (os.path.exists(TESTIMG_DIR)):
    shutil.rmtree(TESTIMG_DIR)
os.mkdir(TESTIMG_DIR)


# Get the dataset using Keras
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()


# create file for list of calibration images
# f = open(os.path.join(CALIB_DIR, IMAGE_LIST_FILE), 'w')


# convert test dataset into image files
for i in range(len(x_test)):
    cv2.imwrite(os.path.join(CALIB_DIR,'calib_' + str(i) + '.png'), x_test[i])
    # f.write('x_test_'+str(i)+'.png\n')

for i in range(len(x_test)):
#    cv2.imwrite(os.path.join(TESTIMG_DIR, str(i) + '.png'), x_test[i])
    cv2.imwrite(os.path.join(TESTIMG_DIR, '_mnist_test' + str(i) + '.png'), x_test[i])

# f.close()

print ('FINISHED GENERATING CALIBRATION & TEST IMAGES')
