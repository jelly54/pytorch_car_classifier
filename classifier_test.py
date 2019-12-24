# -*- coding: utf-8 -*-
from torch import nn
from torch.utils.data import DataLoader
from torchvision import transforms

from data import CarDataset
from network import resnet34
from util import Tester

if __name__ == '__main__':
    # Hyper-params
    data_root = './data/'
    test_csv = './data/test.txt'
    batch_size = 64
    num_workers = 3

    # Set Test parameters
    params = Tester.TestParams()
    params.ckpt = './models/2019-11-28-ckpt_epoch_50.pth'  # './models/ckpt_epoch_400_res34.pth'
    params.categories = 13  # 分类数量

    # 图片转换
    transform = transforms.Compose([
        transforms.Resize(224),  # 缩放图片，保持长宽比不变，最短边的长为224像素,
        transforms.CenterCrop(224),  # 从中间切出 224*224的图片
        transforms.ToTensor(),  # 将图片转换为Tensor,归一化至[0,1]
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # 标准化至[-1,1]
    ])

    # load test data
    print("Loading dataset...")
    test_data = CarDataset(test_csv, data_root, transform=transform)

    test_dataloader = DataLoader(test_data, batch_size=batch_size, shuffle=False, num_workers=num_workers)
    print('val dataset len: {}'.format(len(test_dataloader.dataset)))

    # models
    model = resnet34(pretrained=False, num_classes=1000)  # batch_size=120, 1GPU Memory < 7000M
    model.fc = nn.Linear(512, params.categories)
    # model = resnet101(pretrained=False, num_classes=1000)  # batch_size=60, 1GPU Memory > 9000M
    # model.fc = nn.Linear(512 * 4, 2951)

    # Test
    tester = Tester(model, params, test_dataloader)
    tester.test()
