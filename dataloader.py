import os, shutil
from os import path
import skimage
from skimage.io import imread, imshow
from skimage.transform import resize
from skimage.transform import rotate


import numpy as np

from math import ceil

def get_png_full_path(X_dir):
    
    X_ids = next(os.walk(X_dir))[2] 
    X_ids.sort()
    X_ids = [f for f in X_ids if f.endswith('.png')]
    x_path = [os.path.join(X_dir, x_id) for x_id in X_ids]

    return x_path

def read_image_normalized(img_path, channel):
    
    img = imread(img_path)[:,:,:channel]  # shape (356, 490,3)
    img = img/255.0  
    return img

def Sample_Image_With_Crop(img_path, channel, crop_size, step_size):
    
    img = read_image_normalized(img_path, channel)
    list_imgs = Multi_Crop_image_tolist(img, crop_size, step_size)
    
    # list_imgs, rows, columns
    return list_imgs, int(ceil(img.shape[0]/step_size)), int(ceil(img.shape[1]/step_size)), img.shape[0], img.shape[1]


def Load_Images_With_Crop(img_paths, channel, crop_size, step_size, flip_v=False, flip_h=False):

    # check shape = (0, crop_size, crop_size, channel)
    X_imgdata = np.array([], dtype=np.float32).reshape(0, crop_size, crop_size, channel)

    list_imgs =[]
    for img_path in img_paths: 
       
        #list_crop_imgs, _, _ = Sample_Image_With_Crop(img_path, channel, crop_size, step_size, flip_v, flip_h)   
        img = read_image_normalized(img_path, channel)
        
        if flip_v:
            img = np.flipud(img)
        if flip_h:
            img = np.fliplr(img)
        #list_imgs = Multi_Crop_image_tolist(img, crop_size, step_size)
        #X_imgdata = np.vstack((X_imgdata, list_imgs))

        list_imgs.extend(Multi_Crop_image_tolist(img, crop_size, step_size))
        #[1,2,3].extend([4,5,6]) =[1,2,3,4,5,6] 
        #[1,2,3].append([4,5,6]) =[[1,2,3],[4,5,6]] 

    # doing this is faster!!!, keep crop img in list, then convert to array once!
    X_imgdata = np.stack( list_imgs, axis=0) 
       
    return X_imgdata

def Concate_crop_images(list_imgs0, step_size, list_rows, list_cols, img_height, img_width, channel):
    
    concate_img = np.zeros((img_height, img_width, channel), dtype= np.float64)    
    current_row=0
    current_col=0
    
    for i, crop_img in enumerate(list_imgs0):
        
        x1 = current_col*step_size
        x2 = x1+step_size
        
        y1 = current_row*step_size
        y2 = y1+step_size
        
        # in case that crop_image is at the border area , crop it to the remaining resize in concate_img
        y2 = img_height if y2>img_height else y2
        x2 = img_width if x2>img_width else x2   
           
        #print(i, current_row, current_col, ", y:",y1,y2, ", x:",x1,x2)    
        
        concate_img[y1:y2, x1:x2] = crop_img[0:y2-y1, 0:x2-x1]
        current_col=current_col+1
        
        # move to next rows, reset current_col to 0
        if current_col >= list_cols:
            current_col = 0
            current_row = current_row+1
            
    return concate_img
    #io.imsave( "concate_result.png" , img_as_ubyte(concate_img))
    #plt.imshow(concate_img)    

def Multi_Crop_image_tolist(img, crop_size=128, step_size=64):
    """ return a list of cropped images, 
        for input in datainspect.plot_crop_images_list(list_imgs, list_rows, list_cols)
        (crop a large image to many small pieces)"""
    """ how i do crop the image at the final piece, 
        * padding zero for the remaining area, easy to implement, similar in predict process
        - move crop area to the duplicate the original area?
        - ignore it """

    #list_imgs=[] # we don't know (lazy to calculate) how many image will get, so define it as list 
    
    img_height, img_width, channel = img.shape[0], img.shape[1], img.shape[2]  
    #img = Pad_Image(img, crop_size) # in case that image is smaller than crop size
    
    # Here may not need to pad the raw image...   let it be padded in after crop
    # pad0 = crop_size-img_height if crop_size > img_height else 0
    # pad1 = crop_size-img_width if crop_size > img_width else 0
    # img = np.stack([np.pad(img[:,:,c], ((0,pad0),(0,pad1)), mode='constant', constant_values=0) for c in range(channel)], axis=2)

    # Slice (pad) images
    tiles = [img[x:x+crop_size,y:y+crop_size] for x in range(0, img_height, step_size) for y in range(0, img_width, step_size)]
    #tiles = [img[x:x+M,y:y+N] for x in range(0,img.shape[0],M) for y in range(0,img.shape[1],N)]

    # pad images in list
    for i, tile in enumerate(tiles):
        pad0 = crop_size-tile.shape[0]
        pad1 = crop_size-tile.shape[1]
        #print(tile.shape)
        tiles[i] = np.stack([np.pad(tile[:,:,c], ((0,pad0),(0,pad1)), mode='constant', constant_values=0) for c in range(channel)], axis=2)   

    # crop from top left -> topright -> bottom left -> bottom right
    # for yi in range(0, img_height, step_size):

    #     for xi in range(0, img_width, step_size):

    #         crop_img = img[yi:yi+crop_size, xi:xi+crop_size]
    #         crop_img = Pad_Image(crop_img, crop_size)

    #         list_imgs.append(crop_img)
    #         #crop_imgs_array = np.append(crop_imgs_array, np.array([crop_img]), axis=0)
            
    return tiles

# def Pad_Image(img, crop_size):

#     """ If the image is smaller than the crop size, do padding zero to the crop size"""
#     img_height, img_width, channel = img.shape[0], img.shape[1], img.shape[2]

#     pad_img_h = img_height if img_height > crop_size else crop_size
#     pad_img_w = img_width if img_width > crop_size else crop_size

#     if pad_img_h==img_height and pad_img_w==img_width:
#         #the same size of input, do nothing
#         return img

#     else:
#         # np.zeros fills black color         
#         pad_img = np.zeros((pad_img_h, pad_img_w, channel), dtype= img.dtype)         
#         pad_img[:img_height, :img_width] = img

#         return pad_img

def Filter_nolabel_out(imgs,labels,least_label_px=10):
    
    if imgs.shape[0] != labels.shape[0]:
        print("img != label ",imgs.shape[0],labels.shape[0])
        return
    
    N = imgs.shape[0]
    dropindex=[]
    
    for i in range(N):
        label_pixel = np.sum(labels[i])
        if label_pixel< least_label_px:
            dropindex.append(i)
    #print(len(dropindex))

    imgs = np.delete(imgs, dropindex, axis=0)    
    labels = np.delete(labels, dropindex, axis=0)   
    return imgs, labels
