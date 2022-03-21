#!/usr/bin/python
# -*- coding: UTF-8 -*-
import getopt
import sys

import data
import resnet


def main(argv):
    image_dir = '.'
    model_dir = '.'
    try:
        opts, args = getopt.getopt(argv, "hi:m:", ["image=", "model="])
    except getopt.GetoptError:
        print('train.py -i <image_dir> -m <model_dir>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('train.py -i <image_dir> -m <model_dir>')
            sys.exit()
        elif opt in ("-i", "--image"):
            image_dir = arg
        elif opt in ("-m", "--model"):
            model_dir = arg

    LABEL_LENGTH = 6
    LABELS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    IMAGE_H = 28  # The size of a single character image after scaling, the smaller the training time, the shorter
    IMAGE_W = 28  # The size of a single character image after scaling, the smaller the training time, the shorter
    IMAGE_C = 3   # Number of image channels

    model_file = model_dir + '/model.tfl'

    # Prepare data
    data_sets = data.load(image_dir, IMAGE_H, IMAGE_W, LABEL_LENGTH, LABELS)

    # Build the model
    model = resnet.build(IMAGE_H, IMAGE_W, IMAGE_C, LABELS, model_file, learning_rate=0.01, val_acc_thresh=0.970)

    # to train
    resnet.fit(model, data_sets, model_file, n_epoch=50)


if __name__ == "__main__":
    main(sys.argv[1:])
