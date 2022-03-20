# -*- coding: UTF-8 -*-

import os
import cv2
import numpy as np
import pandas as pd
import tqdm
import base64
from sklearn import model_selection


def read_image(filename, IMAGE_H, IMAGE_W, LABEL_LENGTH):
    image = cv2.imread(filename)

    img_h, img_w = image.shape[:2]
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    kernel = np.ones((2, 2), np.uint8)
    dilate = cv2.dilate(gray, kernel, iterations=1)

    _, thresh = cv2.threshold(dilate, 125, 255, cv2.THRESH_BINARY_INV)

    blur = cv2.GaussianBlur(thresh, (3, 3), 1)
    t_lower = 10  # Lower Threshold
    t_upper = 400  # Upper threshold
    aperture_size = 3  # Aperture size
    l2gradient = True  # Boolean

    canny_output = cv2.Canny(blur, t_lower, t_upper, apertureSize=aperture_size, L2gradient=l2gradient)
    contours, hierarchy = cv2.findContours(canny_output, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    x_min = 0
    x_max = 0
    images = []

    for contour in contours:
        # get rectangle bounding contour
        [x, y, w, h] = cv2.boundingRect(contour)

        if not (w > 20 or h > 20):
            continue

        if x_min == 0:
            x_min = x

        if x > x_min:
            x_min = x

        if x_max == 0:
            x_max = x

        if x_max < x:
            x_max = x

        y_start = 0
        y_end = img_h
        x_start = x
        x_end = x + w
        images.append((x, image[y_start:y_end, x_start:x_end]))

    i = 0
    cur_x = 0
    images.sort(key=lambda x: x[0])
    sorted_images = []
    for img in images:
        if (img[0] - cur_x) < 10:
            continue
        cur_x = img[0]
        img = img[1]
        img = cv2.resize(img, (IMAGE_H, IMAGE_W), interpolation=cv2.INTER_AREA)
        sorted_images.append(img)
        i = i + 1

        if i == LABEL_LENGTH:
            break

    return sorted_images


def decode_image(base64data, IMAGE_H, IMAGE_W, LABEL_LENGTH):
    nparr = np.fromstring(base64.b64decode(str(base64data)), np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    img_h, img_w = image.shape[:2]
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    kernel = np.ones((2, 2), np.uint8)
    dilate = cv2.dilate(gray, kernel, iterations=1)

    _, thresh = cv2.threshold(dilate, 125, 255, cv2.THRESH_BINARY_INV)

    blur = cv2.GaussianBlur(thresh, (3, 3), 1)
    t_lower = 10  # Lower Threshold
    t_upper = 400  # Upper threshold
    aperture_size = 3  # Aperture size
    l2gradient = True  # Boolean

    canny_output = cv2.Canny(blur, t_lower, t_upper, apertureSize=aperture_size, L2gradient=l2gradient)
    contours, hierarchy = cv2.findContours(canny_output, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    x_min = 0
    x_max = 0
    images = []

    for contour in contours:
        # get rectangle bounding contour
        [x, y, w, h] = cv2.boundingRect(contour)

        if not (w > 20 or h > 20):
            continue

        if x_min == 0:
            x_min = x

        if x > x_min:
            x_min = x

        if x_max == 0:
            x_max = x

        if x_max < x:
            x_max = x

        y_start = 0
        y_end = img_h
        x_start = x
        x_end = x + w
        images.append((x, image[y_start:y_end, x_start:x_end]))

    i = 0
    cur_x = 0
    images.sort(key=lambda x: x[0])
    sorted_images = []
    for img in images:
        if (img[0] - cur_x) < 10:
            continue
        cur_x = img[0]
        img = img[1]
        img = cv2.resize(img, (IMAGE_H, IMAGE_W), interpolation=cv2.INTER_AREA)
        sorted_images.append(img)
        i = i + 1

        if i == LABEL_LENGTH:
            break

    return sorted_images


# 验证码去燥
def remove_noise(image):
    return image


def load_data(path, IMAGE_H, IMAGE_W, LABEL_LENGTH, LABELS):
    # OneHot
    def char_to_vec(c):
        y = np.zeros((len(LABELS),))
        y[LABELS.index(c)] = 1.0
        return y

    labels = []
    images = []
    files = []
    fnames = os.listdir(path)
    with tqdm.tqdm(total=len(fnames)) as pbar:
        for i, name in enumerate(fnames):
            print("load file: " + name)
            if name.endswith(".jpg") or name.endswith(".jpeg") or name.endswith(".png"):
                split_images = read_image(os.path.join(path, name), IMAGE_H, IMAGE_W, LABEL_LENGTH)

                if len(split_images) != 6:
                    print("fail to split image :" + os.path.join(path, name))
                    continue

                label = name[:LABEL_LENGTH]
                for k in range(LABEL_LENGTH):
                    labels.append(char_to_vec(label[k]))
                    images.append(remove_noise(split_images[k]))
                    files.append(name)
                pbar.update(1)

    images = np.array(images)
    labels = np.array(labels)
    labels = labels.reshape((labels.shape[0], -1))
    files = np.array(files)

    return images, labels, files


#
class DataSet(object):
    def __init__(self, images, labels):
        assert images.shape[0] == labels.shape[0], (
                "images.shape: %s labels.shape: %s" % (images.shape,
                                                       labels.shape))
        self._num_examples = images.shape[0]
        self._images = images
        self._labels = labels
        self._epochs_completed = 0
        self._index_in_epoch = 0

    @property
    def images(self):
        return self._images

    @property
    def labels(self):
        return self._labels

    @property
    def num_examples(self):
        return self._num_examples

    @property
    def epochs_completed(self):
        return self._epochs_completed

    def next_batch(self, batch_size):
        """Return the next `batch_size` examples from this data set."""
        start = self._index_in_epoch
        self._index_in_epoch += batch_size
        if self._index_in_epoch > self._num_examples:
            # Finished epoch
            self._epochs_completed += 1
            # Shuffle the data
            perm = np.arange(self._num_examples)
            np.random.shuffle(perm)
            self._images = self._images[perm]
            self._labels = self._labels[perm]
            # Start next epoch
            start = 0
            self._index_in_epoch = batch_size
            assert batch_size <= self._num_examples
        end = self._index_in_epoch
        return self._images[start:end], self._labels[start:end]


class DataSets(object):
    pass


# Onehot Convert the encoding back to a string
def onehot2number(label, LABELS):
    return LABELS[np.argmax(label)]


# perform data balance
def balance(images, labels, files, LABELS):
    a = []
    for i, label in enumerate(labels):
        label = onehot2number(label, LABELS)
        a.append([i, label])

    df = pd.DataFrame(a, columns=['i', 'label'])

    new_images = []
    new_labels = []
    new_files = []
    for i in df['i']:
        new_images.append(images[i])
        new_labels.append(labels[i])
        new_files.append(files[i])
    images = np.array(new_images)
    labels = np.array(new_labels)
    files = np.array(new_files)

    return images, labels, files


def make_data_sets(images, labels):
    print("make_data_sets images.shape: %s labels.shape: %s" % (images.shape, labels.shape))

    train_x, test_x, train_y, test_y = model_selection.train_test_split(images, labels, test_size=0.20, random_state=42)

    data_sets = DataSets()
    data_sets.train = DataSet(train_x, train_y)
    data_sets.test = DataSet(test_x, test_y)

    return data_sets


def load(image_dir, IMAGE_H, IMAGE_W, LABEL_LENGTH, LABELS):
    images, labels, files = load_data(image_dir, IMAGE_H, IMAGE_W, LABEL_LENGTH, LABELS)
    images, labels, files = balance(images, labels, files, LABELS)
    data_sets = make_data_sets(images, labels)
    return data_sets
