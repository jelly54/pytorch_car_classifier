# -*- coding: utf-8 -*-
from torch import nn

from network import resnet34
from util import Tester

if __name__ == '__main__':
    # Set Test parameters
    params = Tester.TestParams()
    params.ckpt = './models/2019-11-28-ckpt_epoch_50.pth'  # './models/ckpt_epoch_400_res34.pth'
    params.testdata_dir = './record/testimg/'

    # models
    model = resnet34(pretrained=False, num_classes=1000)  # batch_size=120, 1GPU Memory < 7000M
    model.fc = nn.Linear(512, 2951)
    # model = resnet101(pretrained=False, num_classes=1000)  # batch_size=60, 1GPU Memory > 9000M
    # model.fc = nn.Linear(512 * 4, 2951)

    # Test
    tester = Tester(model, params)
    tester.test()
