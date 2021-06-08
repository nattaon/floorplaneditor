from keras.models import Model
from keras.layers import Input
from keras.layers.convolutional import Conv2D, ZeroPadding2D, Conv2DTranspose,MaxPooling2D
from keras.layers.merge import concatenate
from keras.layers import LeakyReLU, BatchNormalization, Activation, Dropout

def conv5( filter_count, sequence):
	#new_sequence = Conv2D(filter_count, (5, 5), activation='relu', padding='same')(sequence)
    new_sequence = ZeroPadding2D((2,2))(sequence)    
    new_sequence = Conv2D(filter_count, 5, strides=2)(new_sequence)
    new_sequence = BatchNormalization()(new_sequence)       
    new_sequence = Activation(activation='relu')(new_sequence)
    return new_sequence

def conv3( filter_count, sequence):   
    new_sequence = ZeroPadding2D((1,1))(sequence)    
    new_sequence = Conv2D(filter_count, 3, strides=2)(new_sequence)
    new_sequence = BatchNormalization()(new_sequence)       
    new_sequence = Activation(activation='relu')(new_sequence)
    return new_sequence

def flatconv3( filter_count, sequence):   
    new_sequence = ZeroPadding2D((1,1))(sequence)    
    new_sequence = Conv2D(filter_count, 3, strides=1)(new_sequence)
    new_sequence = BatchNormalization()(new_sequence)
    new_sequence = Dropout(0.5)(new_sequence)       
    new_sequence = Activation(activation='relu')(new_sequence)
    return new_sequence

def flatconv3s( filter_count, sequence):   
    new_sequence = ZeroPadding2D((1,1))(sequence)    
    new_sequence = Conv2D(filter_count, 3, strides=1)(new_sequence)
    new_sequence = BatchNormalization()(new_sequence)       
    new_sequence = Activation(activation='sigmoid')(new_sequence)
    return new_sequence

def deconv4( filter_count, sequence):
    #new_sequence = ZeroPadding2D((1,1))(sequence)  
    new_sequence = Conv2DTranspose(filter_count, 2, strides=2)(sequence)
    new_sequence = BatchNormalization()(new_sequence)       
    new_sequence = Activation(activation='relu')(new_sequence)
    return new_sequence    

    #new_sequence = Conv2DTranspose(filter_count, DECONV_FILTER_SIZE, strides=DECONV_STRIDE,
    #                               kernel_initializer='he_uniform')(new_sequence)

def simplify_model():
    
    inputs = Input((256, 256, 3))

    enc1 = conv5( 48, inputs) # 1/2
    enc1 = flatconv3(128, enc1)
    enc1 = flatconv3(128, enc1)

    enc2 = conv3(256, enc1) # 1/4
    enc2 = flatconv3(256, enc2)
    enc2 = flatconv3(256, enc2)

    enc3 = conv3(256, enc2) # 1/8
    enc3 = flatconv3(512, enc3)
    enc3 = flatconv3(1024, enc3)

    enc3 = flatconv3(1024, enc3)
    enc3 = flatconv3(1024, enc3)
    enc3 = flatconv3(1024, enc3)

    enc3 = flatconv3(512, enc3)
    enc3 = flatconv3(256, enc3)

    dec1 = deconv4(256, enc3) # 1/4
    dec1 = flatconv3(256, dec1)
    dec1 = flatconv3(128, dec1)

    dec2 = deconv4(128, dec1) # 1/2
    dec2 = flatconv3(128, dec2)
    dec2 = flatconv3(48, dec2)

    dec3 = deconv4(48, dec2) # 1
    dec3 = flatconv3(24, dec3)
    dec3 = flatconv3s(1, dec3)

    model= Model([inputs], [dec3])

    #model.summary()
    return model
