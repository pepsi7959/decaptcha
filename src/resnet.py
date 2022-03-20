# -*- coding: UTF-8 -*-

# End training early to save the best model
import time

import tensorflow as tf
import tflearn


class EarlyStoppingCallback(tflearn.callbacks.Callback):
    def __init__(self, val_acc_thresh):
        self.val_acc_thresh = val_acc_thresh

    def on_epoch_end(self, training_state):
        if training_state.val_acc >= self.val_acc_thresh and training_state.acc_value >= self.val_acc_thresh:
            raise StopIteration

    def on_train_end(self, training_state):
        self.val_acc = training_state.val_acc
        self.acc_value = training_state.acc_value
        print("Successfully left training! Final model accuracy:", training_state.acc_value)


def build(IMAGE_H, IMAGE_W, IMAGE_C, LABELS, model_file, learning_rate=0.01, val_acc_thresh=0.99):
    img_prep = tflearn.ImagePreprocessing()
    # img_prep.add_featurewise_zero_center(per_channel=True)  # Input image to subtract image mean

    img_aug = tflearn.ImageAugmentation()
    img_aug.add_random_rotation(max_angle=10.0)  # random rotation angle
    # img_aug.add_random_blur(sigma_max=5.0)

    # Building Residual Network
    net = tflearn.input_data(shape=[None, IMAGE_H, IMAGE_W, IMAGE_C],
                             data_preprocessing=img_prep,
                             data_augmentation=img_aug,
                             name='input')

    net = tflearn.conv_2d(net, 16, 3,
                          regularizer='L2',
                          weights_init='variance_scaling',
                          weight_decay=0.0001,
                          name="conv1")  # Convolution processing, 16 convolutions, convolution kernel size of 3, # L2 regularization to reduce overfitting

    net = tflearn.residual_block(net, 1, 16, name="res1")  # 1 Residual layers, output 16 features
    net = tflearn.residual_block(net, 1, 32, downsample=True, name="res2")  # 1 Residual layers, output 32 features, 1/2 dimension reduction
    net = tflearn.residual_block(net, 1, 64, downsample=True, name="res3")  # 1 residual layer, output 64 features, 1/2 dimension reduction

    # Regression
    net = tflearn.fully_connected(net, len(LABELS), activation='softmax')
    mom = tflearn.Momentum(learning_rate, lr_decay=0.1, decay_step=32000, staircase=True)
    net = tflearn.regression(net, optimizer=mom, loss='categorical_crossentropy')

    # Training
    model = tflearn.DNN(net, max_checkpoints=1, tensorboard_verbose=3)

    return model


def load(IMAGE_H, IMAGE_W, IMAGE_C, LABELS, model_file):
    model = build(IMAGE_H, IMAGE_W, IMAGE_C, LABELS, model_file)
    # Load a model
    if tf.gfile.Exists(model_file + '.index'):
        model.load(model_file)
    return model


def fit(model, data_sets, model_file, n_epoch=20):
    start_time = time.time()
    fit_cb = EarlyStoppingCallback(val_acc_thresh=0.998)
    try:
        model.fit(data_sets.train.images,
                  data_sets.train.labels,
                  validation_set=(
                      data_sets.test.images,
                      data_sets.test.labels
                  ),
                  n_epoch=n_epoch,  # The number of feeds for the complete dataset, too many or too few can lead to overfitting or underfitting
                  batch_size=100,  # The number of samples obtained per training
                  shuffle=True,  # Whether to shuffle the data
                  show_metric=True,  # Whether to show the accuracy of the learning process
                  callbacks=fit_cb,  # Used to end training early
                  run_id='vcode_resnet')


    except StopIteration as e:
        print("early stop", e)

    model.save(model_file)
    print('save trained model to ', model_file)

    duration = time.time() - start_time
    print('Training Duration %.3f sec' % duration)
