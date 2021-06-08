import os
import tensorflow as tf
import keras
import keras.backend as K
from keras.optimizers import Adam
from keras.callbacks import ModelCheckpoint, EarlyStopping, TensorBoard
from keras.models import load_model

import matplotlib.pyplot as plt
import numpy as np

from skimage import io
from skimage import img_as_ubyte
from skimage.io import imread, imshow
from skimage.transform import resize, rotate

from sklearn.model_selection import train_test_split

import pickle  # for save train history
import argparse
import warnings
import datetime
import time
import yaml

import datainspect
import dataloader

import segmentation_models as sm
from segmentation_models.metrics import iou_score, f1_score, f2_score, precision, recall

import model.unet02_model_NoneSize as u2m
import model.simplify_model_NoneSize as sim

def create_folder_if_not_exists(path): 
    if not os.path.exists(path): 
        print("createfolder ",path) 
        os.makedirs(path)

def load_config(file_path):
    with open(file_path, 'r') as f:
        config_dict = yaml.full_load(f)
    return config_dict



warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

#Set GPU
configtf = tf.ConfigProto()
#configtf.gpu_options.per_process_gpu_memory_fraction = 0.8
configtf.gpu_options.allow_growth = True
session = tf.Session(config=configtf)
tf.test.gpu_device_name()  
#|   0  Tesla V100-PCIE...  Off  | 00000000:18:00.0 Off |                    0 |
#| N/A   46C    P0    82W / 250W |   5015MiB / 32510MiB |     67%      Default 
# dellalien : conda activate floorplan_segmentation
# python 
# import os
# os.makedirs()
"""
python3 Jan27predictunetcrop.py --config ./config_traincrop/unet02/bceloss/size256val10/config.yaml 
--testpathname ../DatasetFloorplan0/test/test_image20 --predicttotal 1 --weightname weights250.h5

"""
# python3 Jan26predictunetcrop.py --config ./config_traincrop/unet02/bceloss/size256val10/config.yaml --weightname weights250.h5
# python3 Jan26predictunetcrop.py --config ./config_traincrop/unet02/diceloss/size256val10/config.yaml --weightname weights250.h5
parser = argparse.ArgumentParser('Train different parameter of Segmentation model')
parser.add_argument('--config', dest='config', help='config, use this one', type=str, default="")
parser.add_argument('--weightname', dest='weightname', help='weightname', type=str, default="")
parser.add_argument('--testpathindex', dest='testpathindex', help='testpathindex: to select pathindex from config file', type=int, default=-1)
parser.add_argument('--testpathname', dest='testpathname', help='testpathname: to input pathname', type=str, default="")
parser.add_argument('--outputfolder', dest='outputfolder', help='outputfolder: output folder name', type=str, default="")
parser.add_argument('--predicttotal', dest='predicttotal', help='predicttotal: number of image to predict', type=int, default=-1)
args = parser.parse_args()

if(args.config == ""):
    print("Error! Please define --config ")     
if(args.weightname == ""):
    print("Error! Please define --weightname ")   



config_path = args.config
print("Read config: ", config_path)
config_dic = load_config(config_path)
print(yaml.dump(config_dic))

# Define test_dataset_path
if(args.testpathindex == -1):
    # use testpathname    
    if(args.testpathname == ""):
        print("Error! Please define --testpathindex or --testpathname ")  
    else:
        test_dataset_path=args.testpathname
else:
    test_dataset_path = config_dic['test_path'][args.testpathindex]



config_folder = "/".join(config_path.split("/")[:-1])

# print(config_dic['zero_weight'], type(config_dic['zero_weight']))

if(config_dic['model'] == "unet02"):
    model = u2m.unet2(config_dic['input_channel'])

elif(config_dic['model'] == "cnn_simplify"):
    model = sim.simplify_model(config_dic['input_channel'])

elif(config_dic['model'] == "unet_vgg16"):    
    model = sm.Unet('vgg16', input_shape=(None, None, config_dic['input_channel']), encoder_weights=None)   

elif(config_dic['model'] == "unet_resnet34"):    
    model = sm.Unet('resnet34', input_shape=(None, None, config_dic['input_channel']), encoder_weights=None)

else:
    print("Error! No model match. Check config file: model")  

weightpath=os.path.join(config_folder, args.weightname)
weightonlyname = args.weightname.split(".")[0]

model.load_weights(weightpath)    
print("load ",weightpath)




if args.outputfolder == "":
    test_folder_name = test_dataset_path.split("/")[-1]
    if test_folder_name =="": # incase that path end with /
        test_folder_name = test_dataset_path.split("/")[-2]
    #print("test_dataset_path ", test_dataset_path)
    #print("test_folder_name ", test_folder_name)
else:
    test_folder_name =args.outputfolder

output_folder_path = os.path.join(config_folder, test_folder_name, weightonlyname)
channel=config_dic['input_channel']
crop_size = config_dic['input_crop_size']
step_size = config_dic['input_crop_size']
batchsize = config_dic['batch_size'] 

def predict_crop_concate(model, input_image_path, pd_output_path):
    #pd_output_folder = './trainDataSplit/3_test/prediction'

    print("input_image_path", input_image_path)
    print("pd_output_path", pd_output_path)
    create_folder_if_not_exists(pd_output_path)

    dataset_paths = dataloader.get_png_full_path(input_image_path)
    for i, imagepath in enumerate(dataset_paths):    
        list_crop_imgs, num_rows, num_columns, img_height, img_width = \
                        dataloader.Sample_Image_With_Crop(imagepath, channel, crop_size, step_size)      
        # i start from 0, args.predicttotal=-1 as default, to predict 1 image set --predicttotal 1
        if i == args.predicttotal:
            return

        X_imgdata = np.array(list_crop_imgs)       
        #print(X_imgdata.shape)       
        Ys_pred = model.predict(X_imgdata, batchsize)
        #print(Ys_pred.shape)   
        Y_concate = dataloader.Concate_crop_images(Ys_pred, step_size, num_rows, num_columns, img_height, img_width, 1)
        print(Y_concate.shape , Y_concate.dtype)  
        #print(Y_pred[0].shape,Y_pred[0].dtype)      
        #output_img = np.zeros_like(Y_pred[0])

        
        # to create 3channel image from 1 chennel prediction output
        output_img = np.empty((Y_concate.shape[0], Y_concate.shape[1], 3), dtype=Y_concate.dtype)
        #print(output_img.shape,output_img.dtype)
        
        # Create 3 channel image, instead of 1 channel (black and white)
        output_img[:,:,0] = Y_concate.squeeze()
        output_img[:,:,1] = Y_concate.squeeze()
        output_img[:,:,2] = Y_concate.squeeze()
        # cv2.imwrite( save_img_path , img_as_ubyte(output_img)) ok
        
        imagename = imagepath.split("/")[-1]
        save_img_path = os.path.join(pd_output_path,imagename)
        print("save_img_path:",save_img_path)
        io.imsave( save_img_path , img_as_ubyte(output_img), check_contrast=False)
        
        #print(Y_pred[0].shape, output_img.shape ) #(384, 672, 1) (384, 672, 3)
        #break
        #return

predict_crop_concate(model, test_dataset_path, output_folder_path) 
