# -*- coding: utf-8 -*-
import os

import pandas as pd
from PIL import Image
from torch.utils.data import Dataset


class CarDataset(Dataset):

    def __init__(self, csv_file, root_dir, transform=None):
        """
        CarDataset: Custom dataset
        :param csv_file（字符串）:带有注释的csv文件的路径。
        :param root_dir（字符串）:包含所有图像的根目录。
        :param transform（可调用,可选）:应用于样本的可选transform。
        """
        self.landmarks_frame = pd.read_csv(csv_file)
        self.root_dir = root_dir
        self.transform = transform

    def __getitem__(self, index):
        img_path = os.path.join(self.root_dir, self.landmarks_frame.iloc[index, 0])
        label = self.landmarks_frame.iloc[index, 1:]
        image = Image.open(img_path)
        if self.transform:
            image = self.transform(image)
        return image, int(label)

    def __len__(self):
        return len(self.landmarks_frame)

