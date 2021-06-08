from keras.models import Sequential, Model
from keras.layers import Dense, Flatten, Conv2D, Dropout, MaxPooling2D, InputLayer, ZeroPadding2D, Input, MaxPool2D



# create VGG16
def visualkeras_vgg16():
    image_size = 224
    model = Sequential()
    model.add(InputLayer(input_shape=(image_size, image_size, 3)))

    model.add(ZeroPadding2D((1, 1)))
    model.add(Conv2D(64, activation='relu', kernel_size=(3, 3)))
    model.add(ZeroPadding2D((1, 1)))
    model.add(Conv2D(64, activation='relu', kernel_size=(3, 3)))
    #model.add(visualkeras.SpacingDummyLayer())

    model.add(MaxPooling2D((2, 2), strides=(2, 2)))
    model.add(ZeroPadding2D((1, 1)))
    model.add(Conv2D(128, activation='relu', kernel_size=(3, 3)))
    model.add(ZeroPadding2D((1, 1)))
    model.add(Conv2D(128, activation='relu', kernel_size=(3, 3)))
    #model.add(visualkeras.SpacingDummyLayer())

    model.add(MaxPooling2D((2, 2), strides=(2, 2)))
    model.add(ZeroPadding2D((1, 1)))
    model.add(Conv2D(256, activation='relu', kernel_size=(3, 3)))
    model.add(ZeroPadding2D((1, 1)))
    model.add(Conv2D(256, activation='relu', kernel_size=(3, 3)))
    model.add(ZeroPadding2D((1, 1)))
    model.add(Conv2D(256, activation='relu', kernel_size=(3, 3)))
    #model.add(visualkeras.SpacingDummyLayer())

    model.add(MaxPooling2D((2, 2), strides=(2, 2)))
    model.add(ZeroPadding2D((1, 1)))
    model.add(Conv2D(512, activation='relu', kernel_size=(3, 3)))
    model.add(ZeroPadding2D((1, 1)))
    model.add(Conv2D(512, activation='relu', kernel_size=(3, 3)))
    model.add(ZeroPadding2D((1, 1)))
    model.add(Conv2D(512, activation='relu', kernel_size=(3, 3)))
    #model.add(visualkeras.SpacingDummyLayer())

    model.add(MaxPooling2D((2, 2), strides=(2, 2)))
    model.add(ZeroPadding2D((1, 1)))
    model.add(Conv2D(512, activation='relu', kernel_size=(3, 3)))
    model.add(ZeroPadding2D((1, 1)))
    model.add(Conv2D(512, activation='relu', kernel_size=(3, 3)))
    model.add(ZeroPadding2D((1, 1)))
    model.add(Conv2D(512, activation='relu', kernel_size=(3, 3)))
    model.add(MaxPooling2D())
    #model.add(visualkeras.SpacingDummyLayer())

    model.add(Flatten())

    model.add(Dense(4096, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(4096, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(1000, activation='softmax'))
    return model

def mltokyo_vgg16():
    input = Input(shape=(224, 224, 3))

    x = Conv2D(filters=64, kernel_size=3, padding='same', activation='relu')(input)
    x = Conv2D(filters=64, kernel_size=3, padding='same', activation='relu')(x)
    x = MaxPool2D(pool_size=2, strides=2, padding='same')(x)


    x = Conv2D(filters=128, kernel_size=3, padding='same', activation='relu')(x)
    x = Conv2D(filters=128, kernel_size=3, padding='same', activation='relu')(x)
    x = MaxPool2D(pool_size=2, strides=2, padding='same')(x)

    x = Conv2D(filters=256, kernel_size=3, padding='same', activation='relu')(x)
    x = Conv2D(filters=256, kernel_size=3, padding='same', activation='relu')(x)
    x = Conv2D(filters=256, kernel_size=3, padding='same', activation='relu')(x)
    x = MaxPool2D(pool_size=2, strides=2, padding='same')(x)

    x = Conv2D(filters=512, kernel_size=3, padding='same', activation='relu')(x)
    x = Conv2D(filters=512, kernel_size=3, padding='same', activation='relu')(x)
    x = Conv2D(filters=512, kernel_size=3, padding='same', activation='relu')(x)
    x = MaxPool2D(pool_size=2, strides=2, padding='same')(x)

    x = Conv2D(filters=512, kernel_size=3, padding='same', activation='relu')(x)
    x = Conv2D(filters=512, kernel_size=3, padding='same', activation='relu')(x)
    x = Conv2D(filters=512, kernel_size=3, padding='same', activation='relu')(x)
    x = MaxPool2D(pool_size=2, strides=2, padding='same')(x)

    x = Flatten()(x)
    x = Dense(units=4096, activation='relu')(x)
    x = Dense(units=4096, activation='relu')(x)
    output = Dense(units=1000, activation='softmax')(x)

    model = Model(inputs=input, outputs=output)   
    return model
