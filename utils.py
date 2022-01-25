import scipy.misc
import numpy as np
import copy
import os
import cv2
from glob import glob
from tqdm import tqdm
class ImagePool(object):
    def __init__(self, maxsize=50):
        self.maxsize = maxsize
        self.num_img = 0
        self.images = []

    def __call__(self, image):
        if self.maxsize <= 0:
            return image
        if self.num_img < self.maxsize:
            self.images.append(image)
            self.num_img += 1
            return image
        if np.random.rand() > 0.5:
            idx = int(np.random.rand()*self.maxsize)
            tmp1 = copy.copy(self.images[idx])[0]
            self.images[idx][0] = image[0]
            idx = int(np.random.rand()*self.maxsize)
            tmp2 = copy.copy(self.images[idx])[1]
            self.images[idx][1] = image[1]
            return [tmp1, tmp2]
        else:
            return image

def load_test_data(image_path, fine_size=256):
    img = imread(image_path)
    img = scipy.misc.imresize(img, [fine_size, fine_size*2])
    img = img/127.5 - 1
    return img

def check_folder(path):
    if not os.path.exists(path):
        os.mkdir(path)

def load_train_data(image_path, load_size=286, fine_size=256, is_testing=False):
    img_A = imread(image_path[0])
    img_B = imread(image_path[1])
    
    if not is_testing:
        alpha1 = np.random.uniform(0.9, 1.1)
        alpha2 = np.random.uniform(0.9, 1.1)
        new_loadsize = int(np.ceil(load_size*alpha1))
        new_loadsize2 = int(np.ceil(load_size*2*alpha2))
        img_A = scipy.misc.imresize(img_A, [new_loadsize, new_loadsize2])
        img_B = scipy.misc.imresize(img_B, [new_loadsize, new_loadsize2])
        h1 = int(np.ceil(np.random.uniform(1e-2, new_loadsize-fine_size)))
        w1 = int(np.ceil(np.random.uniform(1e-2, new_loadsize2-(fine_size*2))))
        img_A = img_A[h1:h1+fine_size, w1:w1+fine_size*2]
        img_B = img_B[h1:h1+fine_size, w1:w1+fine_size*2]

        if np.random.random() > 0.5:
            img_A = np.fliplr(img_A)
            img_B = np.fliplr(img_B)

    else:
        img_A = scipy.misc.imresize(img_A, [fine_size, fine_size*2])
        img_B = scipy.misc.imresize(img_B, [fine_size, fine_size*2])

    img_A = img_A/127.5 - 1.
    img_B = img_B/127.5 - 1.
    img_AB = np.concatenate((img_A, img_B), axis=2)
    return img_AB

# -----------------------------

def get_image(image_path, image_size, is_crop=True, resize_w=64, is_grayscale = False):
    return transform(imread(image_path, is_grayscale), image_size, is_crop, resize_w)

def save_images(images, size, image_path):
    return imsave(inverse_transform(images), size, image_path)

def imread(path, is_grayscale = False):
    if (is_grayscale):
        return scipy.misc.imread(path, flatten = True).astype(np.float)
    else:
        return scipy.misc.imread(path, mode='RGB').astype(np.float)

def merge_images(images, size):
    return inverse_transform(images)

def merge(images, size):
    h, w = images.shape[1], images.shape[2]
    img = np.zeros((h * size[0], w * size[1], 3))
    for idx, image in enumerate(images):
        i = idx % size[1]
        j = idx // size[1]
        img[j*h:j*h+h, i*w:i*w+w, :] = image

    return img

def imsave(images, size, path):
    return scipy.misc.imsave(path, merge(images, size))

def center_crop(x, crop_h, crop_w,
                resize_h=64, resize_w=64):
  if crop_w is None:
    crop_w = crop_h
  h, w = x.shape[:2]
  j = int(round((h - crop_h)/2.))
  i = int(round((w - crop_w)/2.))
  return scipy.misc.imresize(
      x[j:j+crop_h, i:i+crop_w], [resize_h, resize_w])

def transform(image, npx=64, is_crop=True, resize_w=64):
    # npx : # of pixels width/height of image
    if is_crop:
        cropped_image = center_crop(image, npx, resize_w=resize_w)
    else:
        cropped_image = image
    return np.array(cropped_image)/127.5 - 1.

def inverse_transform(images):
    return (images+1.)/2.



def vector_max_min(img_path_A, img_path_B):
    """
    Calculate Brightness, Contrast, Saturation's max and min
    If you calculate already, just turn it off
    """
    brightness_max = 0
    contrast_max = 0
    saturation_max = 0
    brightness_min = 1
    contrast_min = 1
    saturation_min = 1
    imgs = glob(img_path_A)
    for img in tqdm(imgs):
        im = cv2.imread(img)
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
        gray = gray.astype(np.float) / 255.
        brightness = np.mean(gray)
        contrast = np.sqrt(np.mean(np.square(gray - brightness)))
        hsv = hsv[:,:,1].astype(np.float) / 255.
        saturation = np.mean(hsv)
  
        if brightness > brightness_max:
            brightness_max = brightness
        if brightness < brightness_min:
            brightness_min = brightness
        
        if contrast > contrast_max:
            contrast_max = contrast
        if contrast < contrast_min:
            contrast_min = contrast
        
        if saturation > saturation_max:
            saturation_max = saturation
        if saturation < saturation_min:
            saturation_min = saturation

    
    imgs = glob(img_path_B)
    
    for img in tqdm(imgs):
        im = cv2.imread(img)
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
        gray = gray.astype(np.float) / 255.
        brightness = np.mean(gray)
        contrast = np.sqrt(np.mean(np.square(gray - brightness)))
        hsv = hsv[:,:,1].astype(np.float) / 255.
        saturation = np.mean(hsv)
  
        if brightness > brightness_max:
            brightness_max = brightness
        if brightness < brightness_min:
            brightness_min = brightness
        
        if contrast > contrast_max:
            contrast_max = contrast
        if contrast < contrast_min:
            contrast_min = contrast
        
        if saturation > saturation_max:
            saturation_max = saturation
        if saturation < saturation_min:
            saturation_min = saturation

    return brightness_max, contrast_max, saturation_max, brightness_min, contrast_min, saturation_min