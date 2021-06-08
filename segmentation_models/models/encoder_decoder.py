from keras_applications import get_submodules_from_kwargs

from ._common_blocks import Conv2dBn
from ._utils import freeze_model, filter_keras_submodules
from ..backbones.backbones_factory import Backbones

backend = None
layers = None
models = None
keras_utils = None


# ---------------------------------------------------------------------
#  Utility functions
# ---------------------------------------------------------------------

def get_submodules():
    return {
        'backend': backend,
        'models': models,
        'layers': layers,
        'utils': keras_utils,
    }


# ---------------------------------------------------------------------
#  Blocks
# ---------------------------------------------------------------------

def Conv3x3BnReLU(filters, use_batchnorm, name=None):
    kwargs = get_submodules()

    def wrapper(input_tensor):
        return Conv2dBn(
            filters,
            kernel_size=3,
            activation='relu',
            kernel_initializer='he_uniform',
            padding='same',
            use_batchnorm=use_batchnorm,
            name=name,
            **kwargs
        )(input_tensor)

    return wrapper


def Conv1x1BnReLU(filters, use_batchnorm, name=None):
    kwargs = get_submodules()

    def wrapper(input_tensor):
        return Conv2dBn(
            filters,
            kernel_size=1,
            activation='relu',
            kernel_initializer='he_uniform',
            padding='same',
            use_batchnorm=use_batchnorm,
            name=name,
            **kwargs
        )(input_tensor)

    return wrapper


def DecoderUpsamplingX2Block(filters, stage, use_batchnorm):
    conv_block1_name = 'decoder_stage{}a'.format(stage)
    conv_block2_name = 'decoder_stage{}b'.format(stage)
    conv_block3_name = 'decoder_stage{}c'.format(stage)
    up_name = 'decoder_stage{}_upsampling'.format(stage)
    add_name = 'decoder_stage{}_add'.format(stage)

    channels_axis = 3 if backend.image_data_format() == 'channels_last' else 1

    def wrapper(input_tensor, skip=None):
        input_filters = backend.int_shape(input_tensor)[channels_axis]
        output_filters = backend.int_shape(skip)[channels_axis] if skip is not None else filters

        x = Conv1x1BnReLU(input_filters // 4, use_batchnorm, name=conv_block1_name)(input_tensor)
        x = layers.UpSampling2D((2, 2), name=up_name)(x)
        x = Conv3x3BnReLU(input_filters // 4, use_batchnorm, name=conv_block2_name)(x)
        x = Conv1x1BnReLU(output_filters, use_batchnorm, name=conv_block3_name)(x)

        #if skip is not None:
        #    x = layers.Add(name=add_name)([x, skip])
        return x

    return wrapper


def DecoderTransposeX2Block(filters, stage, use_batchnorm):
    conv_block1_name = 'decoder_stage{}a'.format(stage)
    transpose_name = 'decoder_stage{}b_transpose'.format(stage)
    bn_name = 'decoder_stage{}b_bn'.format(stage)
    relu_name = 'decoder_stage{}b_relu'.format(stage)
    conv_block3_name = 'decoder_stage{}c'.format(stage)
    add_name = 'decoder_stage{}_add'.format(stage)

    channels_axis = bn_axis = 3 if backend.image_data_format() == 'channels_last' else 1

    def wrapper(input_tensor, skip=None):
        input_filters = backend.int_shape(input_tensor)[channels_axis]
        output_filters = backend.int_shape(skip)[channels_axis] if skip is not None else filters

        x = Conv1x1BnReLU(input_filters // 4, use_batchnorm, name=conv_block1_name)(input_tensor)
        x = layers.Conv2DTranspose(
            filters=input_filters // 4,
            kernel_size=(4, 4),
            strides=(2, 2),
            padding='same',
            name=transpose_name,
            use_bias=not use_batchnorm,
        )(x)

        if use_batchnorm:
            x = layers.BatchNormalization(axis=bn_axis, name=bn_name)(x)

        x = layers.Activation('relu', name=relu_name)(x)
        x = Conv1x1BnReLU(output_filters, use_batchnorm, name=conv_block3_name)(x)

        if skip is not None:
            x = layers.Add(name=add_name)([x, skip])

        return x

    return wrapper


# ---------------------------------------------------------------------
#  Decoder
# ---------------------------------------------------------------------

def build_encodeco(
        backbone,
        decoder_block,
        skip_connection_layers,
        decoder_filters=(256, 128, 64, 32, 16),
        n_upsample_blocks=5,
        classes=1,
        activation='sigmoid',
        use_batchnorm=True,
):
    input_ = backbone.input
    x = backbone.output

    # extract skip connections
    skips = ([backbone.get_layer(name=i).output if isinstance(i, str)
              else backbone.get_layer(index=i).output for i in skip_connection_layers])

    # add center block if previous operation was maxpooling (for vgg models)
    if isinstance(backbone.layers[-1], layers.MaxPooling2D):
        x = Conv3x3BnReLU(512, use_batchnorm, name='center_block1')(x)
        x = Conv3x3BnReLU(512, use_batchnorm, name='center_block2')(x)

    # building decoder blocks
    for i in range(n_upsample_blocks):

        if i < len(skips):
            skip = skips[i]
        else:
            skip = None

        x = decoder_block(decoder_filters[i], stage=i, use_batchnorm=use_batchnorm)(x, skip)

    # model head (define number of output classes)
    x = layers.Conv2D(
        filters=classes,
        kernel_size=(3, 3),
        padding='same',
        use_bias=True,
        kernel_initializer='glorot_uniform'
    )(x)
    x = layers.Activation(activation, name=activation)(x)

    # create keras model instance
    model = models.Model(input_, x)

    return model


# ---------------------------------------------------------------------
#  Encodeco Model
# ---------------------------------------------------------------------

def Encodeco(
        backbone_name='vgg16',
        input_shape=(None, None, 3),
        classes=1,
        activation='sigmoid',
        weights=None,
        encoder_weights='imagenet',
        encoder_freeze=False,
        encoder_features='default',
        decoder_block_type='upsampling',
        decoder_filters=(None, None, None, None, 16),
        decoder_use_batchnorm=True,
        **kwargs
):
    """
    """

    global backend, layers, models, keras_utils
    submodule_args = filter_keras_submodules(kwargs)
    backend, layers, models, keras_utils = get_submodules_from_kwargs(submodule_args)

    if decoder_block_type == 'upsampling':
        decoder_block = DecoderUpsamplingX2Block
    elif decoder_block_type == 'transpose':
        decoder_block = DecoderTransposeX2Block
    else:
        raise ValueError('Decoder block type should be in ("upsampling", "transpose"). '
                         'Got: {}'.format(decoder_block_type))

    backbone = Backbones.get_backbone(
        backbone_name,
        input_shape=input_shape,
        weights=encoder_weights,
        include_top=False,
        **kwargs,
    )

    if encoder_features == 'default':
        encoder_features = Backbones.get_feature_layers(backbone_name, n=4)

    model = build_encodeco(
        backbone=backbone,
        decoder_block=decoder_block,
        skip_connection_layers=encoder_features,
        decoder_filters=decoder_filters,
        classes=classes,
        activation=activation,
        n_upsample_blocks=len(decoder_filters),
        use_batchnorm=decoder_use_batchnorm,
    )

    # lock encoder weights for fine-tuning
    if encoder_freeze:
        freeze_model(backbone, **kwargs)

    # loading model weights
    if weights is not None:
        model.load_weights(weights)

    return model
