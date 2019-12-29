# -*- coding: utf-8 -*-
from __future__ import print_function

import os

import torch
import torch.nn.functional as F
import torchvision.transforms.functional as tv_F
from PIL import Image

from .log import logger


class TestParams(object):
    # Number of categories
    categories = 2

    # params based on your local env
    device = torch.device('cpu')
    gpus = []

    # loading existing checkpoint
    ckpt = './models/ckpt_epoch_50.pth'  # path to the ckpt file


class Tester(object):
    TestParams = TestParams

    def __init__(self, model, test_params, test_data):
        assert isinstance(test_params, TestParams)
        self.params = test_params

        # Data loaders
        self.test_data = test_data

        # load model
        self.model = model

        ckpt = self.params.ckpt
        if ckpt is not None:
            self._load_ckpt(ckpt)
            logger.info('Load ckpt from {}'.format(ckpt))

        # set CUDA_VISIBLE_DEVICES, 1 GPU is enough
        if len(self.params.gpus) > 0 and torch.cuda.is_available():
            self.params.device = torch.device("cuda")
            gpu_test = str(self.params.gpus[0])
            os.environ['CUDA_VISIBLE_DEVICES'] = gpu_test
            logger.info('Set CUDA_VISIBLE_DEVICES to {}...'.format(gpu_test))

        self.model.to(self.params.device)

        # release empty cache
        torch.cuda.empty_cache()

        self.model.eval()

    def test(self):

        for step, (data, label) in enumerate(self.test_data):
            print('Processing image: ' + str(step))
            inputs = torch.unsqueeze(data, 0).to(self.params.device)

            output = self.model(inputs)
            score = F.softmax(output, dim=1)
            _, prediction = torch.max(score.data, dim=1)

            print('Prediction number: %s , label: %d ' % (str(prediction[0]), label))

    def _load_ckpt(self, ckpt):
        self.model.load_state_dict(torch.load(ckpt))
