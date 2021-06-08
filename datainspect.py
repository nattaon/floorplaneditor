import os, shutil
from os import path
import skimage
from skimage.io import imread, imshow, imsave
from skimage import img_as_ubyte
from skimage.transform import resize
from skimage.transform import rotate
import numpy as np
import matplotlib.pyplot as plt
from  matplotlib import colors
import pickle

def get_images_size(dataset_paths):

    imgsize_array = np.empty((0, 2), int) #(width, height)

    for filepath in dataset_paths:
        im = imread(filepath)
        (height, width, channels) = im.shape
        imgsize_array = np.append(imgsize_array, np.array([[width,height]]), axis=0)
        #sizelist.append([width,height])
        #img_size[i,0] = width
        #img_size[i,1] = height
    return imgsize_array

def plot_img_size_variation(imgsize_array, savename=None): #"plot_img_size_variation.png"
    
    img_size_unq , img_size_count = np.unique(imgsize_array, axis=0, return_counts=True)
    x = img_size_unq[:,0]
    y = img_size_unq[:,1]
    z = img_size_count
    cmap=plt.cm.rainbow
    norm = colors.BoundaryNorm(np.arange(np.min(img_size_count),np.max(img_size_count),1), cmap.N)
    fig = plt.figure(figsize=(20,10), facecolor='w', edgecolor='k')
    plt.scatter(x,y,c=z,cmap=cmap,norm=norm,s=50,edgecolor='b')#none
    plt.colorbar(ticks=np.arange(1,15))#ticks=np.linspace(-2,2,5)
    plt.title("Total image = "+str(len(imgsize_array)))
    plt.xlabel("Image width")
    plt.ylabel("Image height")  

    if savename is not None:
        plt.savefig(savename,transparent=False,bbox_inches='tight')
    else:
        plt.show()  

def plt_imshow_squeeze_if_channel_eq1(img):
    if img.shape[2]==1:
        plt.imshow(img.squeeze(),cmap = 'gray')
    else:
        plt.imshow(img)

def plot_crop_images_list(crop_images, rows, columns,figsizemultiply=4):
    """ crop_images: a list of image(height*width)
    rows : the number of division in height axis
    columns: the number of division in width axis
    """
    fig = plt.figure(figsize=(columns*figsizemultiply,rows*figsizemultiply), facecolor='w', edgecolor='k')

    for i in range(0, len(crop_images)):
        fig.add_subplot(rows, columns, i+1)
        plt_imshow_squeeze_if_channel_eq1(crop_images[i])
        # if crop_images[i].shape[2]==1:
        #     plt.imshow(crop_images[i].squeeze(),cmap = 'gray')
        # else:
        #     plt.imshow(crop_images[i])

    # the following lines cause a big white space between label and images. need to adjust!
    #fig.suptitle("Total crop = "+str(len(crop_images)))
    #fig.text(0.5, 0.04, "column = "+str(columns), ha='center')
    #fig.text(0.04, 0.5, "row = "+str(rows), va='center', rotation='vertical') 
    plt.show()
    fig.savefig("plot_crop_images_list.png",bbox_inches='tight')    #transparent=False,

# ## plot_crop_images_list() and plot_crop_images_array() has a similar code .. should merge!!

def plot_crop_images_array(crop_images, rows, columns,figsizemultiply=4):
    #plot_crop_images_array(labedata0[10:,:,:],10,10)
    #plot_crop_images_array(labedata0,10,10)
    """ crop_images: an array of image(total,height,width)
    rows : the number of division in height axis
    columns: the number of division in width axis
    """
    fig = plt.figure(figsize=(columns*figsizemultiply,rows*figsizemultiply), facecolor='w', edgecolor='k')

    for i in range(0, rows*columns):
        fig.add_subplot(rows, columns, i+1)
        plt_imshow_squeeze_if_channel_eq1(crop_images[i])
        # if crop_images[i].shape[2]==1:
        #     plt.imshow(crop_images[i].squeeze(),cmap = 'gray') # remove the chanel if it = 1
        # else:
        #     plt.imshow(crop_images[i])

    plt.show()

def plot_pair_img_label(img,label,figsize=(8,4)):
    """ plot a pairs of img&label"""

    fig=plt.figure(figsize=figsize)
    columns = 2
    rows = 1


    fig.add_subplot(rows, columns, 1)
    plt_imshow_squeeze_if_channel_eq1(img)
    #plt.imshow(img)

    fig.add_subplot(rows, columns, 2)
    plt_imshow_squeeze_if_channel_eq1(label)
    #plt.imshow(label, cmap=plt.cm.gray)  

    plt.show()   

    print("img,label shape:", img.shape, label.shape) 

def save_pair_imgs_labels(imgs, labels, savefoldername):
    
    if imgs.ndim !=4 or labels.ndim!=4:
        print("imgs or labels is not 4d array",imgs.shape, labels.shape )
        return
    
    total = imgs.shape[0]
    size = imgs.shape[1]
    dtypee =imgs.dtype
    # create output folder if not exist
    if not os.path.exists(savefoldername):
        os.makedirs(savefoldername)

    for i in range(total):
        #print(i, np.min(imgs[i]), np.max(imgs[i]))
        
        separator = np.full((size, 1, 1), 0.5 ,dtype=dtypee)
        #print(imgs[i].shape, separator.shape,labels[i].shape)
        pair_img = np.concatenate([imgs[i], separator, labels[i]], 1)
        save_img_path = os.path.join(savefoldername,str(i).zfill(4)+".png")
        imsave( save_img_path , img_as_ubyte(pair_img), check_contrast=False)
    
    print("done saving ", total, "pair img-label. At",savefoldername)


def plot_pair_imgs_labels(imgs, labels, rows=1, columns=2,figsizemultiply=4):
    """ 
    plot multiple pairs of img&label
    user define rows : as the number of pair to show 
    imgs and labels can assign more than rows number, it will be cut off
    """

    if imgs.ndim !=4 or labels.ndim!=4:
        print("imgs or labels is not 4d array",imgs.shape, labels.shape )
        return
    
    if imgs.shape[0] != labels.shape[0]:
        print("img != label ",imgs.shape[0],labels.shape[0])
        return
    
    if imgs.shape[0] < rows:
        print("imgs.shape[0] < rows ", imgs.shape[0], rows)      
        return
    
    fig=plt.figure(figsize=(columns*figsizemultiply,rows*figsizemultiply))        
    
    #columns = 2
    #rows = 16
    for i in range(0, rows):
        #img = np.random.randint(10, size=(h,w))

        fig.add_subplot(rows, columns, i*2+1)
        plt_imshow_squeeze_if_channel_eq1(imgs[i])
        #plt.imshow(imgs[i])

        fig.add_subplot(rows, columns, i*2+2)
        plt_imshow_squeeze_if_channel_eq1(labels[i])
        #plt.imshow(labels[i].squeeze(), cmap=plt.cm.gray)  

    plt.show()    

def plotcomparisongraph_line_marker(markerat, xval, y1val, y2val, y1label, y2label, titlename):
    if markerat == "max":
        mark_val_y2 = max(y2val)
    elif markerat == "min":
        mark_val_y2 = min(y2val)
    else:
        print("markerat keyword not recognize, please define max or min")

    mark_ind_y2 = y2val.index(mark_val_y2)

    # plt.figure() # new figure
    plt.plot(xval, y1val, 'r--', label=y1label)
    plt.plot(xval, y2val, '-bD', label=y2label, markevery=[mark_ind_y2])
    plt.ylim(0.0, 1.0)
    plt.title(titlename + " best index = " + str(mark_ind_y2+1))
    plt.legend()

def plot_history(history_name):

    with open(history_name, 'rb') as file_pi:
        history = pickle.load(file_pi)

    print(history.keys())

    epochs = range(len(history['loss']))
    figtitle = history_name

    ######## Plot training graph ##############

    fig = plt.figure(num=None, figsize=(12, 4), dpi=100, facecolor='w', edgecolor='k')
    fig.suptitle(figtitle)

    # loss, val_loss
    plt.subplot(1, 2, 1)
    plotcomparisongraph_line_marker("min", epochs, history['loss'], history['val_loss'], 'Training', 'Validation',
                                    'loss')

    # acc, val_acc
    plt.subplot(1, 2, 2)
    plotcomparisongraph_line_marker("max", epochs, history['acc'], history['val_acc'], 'Training',
                                    'Validation', 'accuracy')

    plt.savefig(history_name + '.png')  

    
