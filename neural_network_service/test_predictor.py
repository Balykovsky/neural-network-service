import time
import platform
import torch
from random import shuffle

import cv2
import os
from multiprocessing import freeze_support
import numpy as np
from torchvision import transforms

class TestPredictor:
    def __init__(self, path_list):
        self.path_list = path_list

    def predict(self, callback):
        for img in self.path_list:
            time.sleep(3)
            callback(target=img[-4:])