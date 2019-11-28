# -*- coding: utf-8 -*-
from __future__ import print_function

import os

import torch
import torch.nn.functional as F
import torchvision.transforms.functional as tv_F
from PIL import Image
from torch.autograd import Variable

from .log import logger


class TestParams(object):
    # params based on your local env
    gpus = []  # default to use CPU mode

    # loading existing checkpoint
    ckpt = './models/ckpt_epoch_50.pth'  # path to the ckpt file

    testdata_dir = './record/testimg/'


class Tester(object):
    TestParams = TestParams

    def __init__(self, model, test_params):
        assert isinstance(test_params, TestParams)
        self.params = test_params

        # load model
        self.model = model
        ckpt = self.params.ckpt
        if ckpt is not None:
            self._load_ckpt(ckpt)
            logger.info('Load ckpt from {}'.format(ckpt))

        # set CUDA_VISIBLE_DEVICES, 1 GPU is enough
        if len(self.params.gpus) > 0:
            gpu_test = str(self.params.gpus[0])
            os.environ['CUDA_VISIBLE_DEVICES'] = gpu_test
            logger.info('Set CUDA_VISIBLE_DEVICES to {}...'.format(gpu_test))
            self.model = self.model.cuda()

        self.model.eval()

    def test(self):

        img_list = os.listdir(self.params.testdata_dir)

        for img_name in img_list:
            print('Processing image: ' + img_name)

            # img = Image.open(os.path.join(self.params.testdata_dir, img_name))
            img_name = os.path.join(self.params.testdata_dir, img_name)
            img = Image.open(img_name)

            img = tv_F.to_tensor(tv_F.resize(img, (224, 224)))
            img = tv_F.normalize(img, [0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            img_input = Variable(torch.unsqueeze(img, 0))
            if len(self.params.gpus) > 0:
                img_input = img_input.cuda()

            output = self.model(img_input)
            score = F.softmax(output, dim=1)
            _, prediction = torch.max(score.data, dim=1)

            print('Prediction number: ' + str(prediction[0]))

    def _load_ckpt(self, ckpt):
        self.model.load_state_dict(torch.load(ckpt))
        # 使用cpu预测
        # self.model.load_state_dict(torch.load(ckpt, map_location=torch.device('cpu')), False)
