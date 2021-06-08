import os
import tensorflow as tf
import numpy as np
from skimage.io import imread, imsave
from skimage import img_as_ubyte
import warnings
import segmentation_models as sm
import dataloader
#MODEL_PATH= "model/"

class tfpredict(object):
    def __init__(self, parent=None):
        self.weightpath="model/weights1000.h5"
        resultfolder = "predictresult"
        if not os.path.exists(resultfolder): 
            os.makedirs(resultfolder)
        self.resultfolder = resultfolder

    def predict(self, imagepath):
        warnings.filterwarnings('ignore', category=DeprecationWarning)
        warnings.filterwarnings('ignore', category=FutureWarning)
        tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
        configtf = tf.ConfigProto()
        configtf.gpu_options.allow_growth = True
        session = tf.Session(config=configtf)
        #tf.test.gpu_device_name()   
         

        channel=3
        crop_size = 256
        step_size = 256
        batchsize = 8      

        model = sm.Unet('vgg16', input_shape=(None, None, channel), encoder_weights=None)   
        model.load_weights(self.weightpath)


        list_crop_imgs, num_rows, num_columns, img_height, img_width = \
                        dataloader.Sample_Image_With_Crop(imagepath, channel, crop_size, step_size) 
        X_imgdata = np.array(list_crop_imgs)  
        Ys_pred = model.predict(X_imgdata, batchsize)
        Y_concate = dataloader.Concate_crop_images(Ys_pred, step_size, num_rows, num_columns, img_height, img_width, 1)
        print(Y_concate.shape , Y_concate.dtype)

        output_img = np.empty((Y_concate.shape[0], Y_concate.shape[1], 3), dtype=Y_concate.dtype)
        output_img[:,:,0] = Y_concate.squeeze()
        output_img[:,:,1] = Y_concate.squeeze()
        output_img[:,:,2] = Y_concate.squeeze()
        imagename = imagepath.split("/")[-1]
        save_img_path = os.path.join(self.resultfolder,imagename)         
        print("save_img_path:",save_img_path)
        imsave( save_img_path , img_as_ubyte(output_img), check_contrast=False)

        return save_img_path
