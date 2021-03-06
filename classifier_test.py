# -*- coding: utf-8 -*-
from torch import nn

from network import resnet101
from util import Tester

# Set Test parameters
params = Tester.TestParams()
params.gpus = [0]  # set 'params.gpus=[]' to use CPU model. if len(params.gpus)>1, default to use params.gpus[0] to test
params.ckpt = './models/ckpt_epoch_800_res101.pth'  # './models/ckpt_epoch_400_res34.pth'
params.testdata_dir = './testimg/'

# models
# model = resnet34(pretrained=False, num_classes=1000)  # batch_size=120, 1GPU Memory < 7000M
# model.fc = nn.Linear(512, 6)
model = resnet101(pretrained=False, num_classes=1000)  # batch_size=60, 1GPU Memory > 9000M
model.fc = nn.Linear(512 * 4, 6)

# Test
tester = Tester(model, params)
tester.test()
