# -*- coding: utf-8 -*-
import torch
from torch import nn
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch.utils.data import DataLoader
from torchvision import transforms

from dataset import CarDataset
from network import resnet34
from util import Trainer

if __name__ == '__main__':
    # Hyper-params
    data_root = './record/images/'
    train_csv = './record/train.txt'
    val_csv = './record/val.txt'
    model_path = './models/'
    batch_size = 128  # batch_size per GPU, if use GPU mode;
    num_workers = 3

    init_lr = 0.01
    lr_decay = 0.8
    momentum = 0.9
    weight_decay = 0.000
    nesterov = True

    # Set Training parameters
    params = Trainer.TrainParams()
    params.max_epoch = 500
    params.criterion = nn.CrossEntropyLoss()
    params.save_dir = model_path
    params.ckpt = None  # 加载训练好的模型
    params.save_freq_epoch = 50

    # 图片转换 原图：(135, 202, 3)
    transform = transforms.Compose([
        transforms.Resize(224),  # 缩放图片，保持长宽比不变，最短边的长为224像素,
        transforms.CenterCrop(224),  # 从中间切出 224*224的图片
        transforms.ToTensor(),  # 将图片转换为Tensor,归一化至[0,1]
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # 标准化至[-1,1]
    ])

    # load data
    print("Loading dataset...")
    train_data = CarDataset(train_csv, data_root, transform=transform)
    val_data = CarDataset(val_csv, data_root, transform=transform)

    batch_size = batch_size if torch.cuda.device_count() == 0 else batch_size * torch.cuda.device_count()

    train_dataloader = DataLoader(train_data, batch_size=batch_size, shuffle=True, num_workers=num_workers)
    print('train dataset len: {}'.format(len(train_dataloader.dataset)))

    val_dataloader = DataLoader(val_data, batch_size=batch_size, shuffle=False, num_workers=num_workers)
    print('val dataset len: {}'.format(len(val_dataloader.dataset)))

    # models
    model = resnet34(pretrained=False, modelpath=model_path, num_classes=1000)  # batch_size=120, 1GPU Memory < 7000M
    model.fc = nn.Linear(512, 2951)
    # model = resnet101(pretrained=True, modelpath=model_path, num_classes=1000)  # batch_size=60, 1GPU Memory > 9000M
    # model.fc = nn.Linear(512 * 4, 2951)

    # optimizer
    trainable_vars = [param for param in model.parameters() if param.requires_grad]
    print("Training with sgd")
    params.optimizer = torch.optim.SGD(trainable_vars, lr=init_lr,
                                       momentum=momentum,
                                       weight_decay=weight_decay,
                                       nesterov=nesterov)

    # optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)
    # optimizer = optim.Adam([var1, var2], lr=0.0001)

    # Train
    params.lr_scheduler = ReduceLROnPlateau(params.optimizer, 'min', factor=lr_decay, patience=10, cooldown=10,
                                            verbose=True)
    trainer = Trainer(model, params, train_dataloader, val_dataloader)
    trainer.train()
