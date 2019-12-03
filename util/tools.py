# -*- coding: utf-8 -*-
import os

import math


def listdir(path, list_name):
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            listdir(file_path, list_name)
        else:
            list_name.append(file_path.replace("\\", "/"))
    return list_name


def list2file(list_name, file_name, lable):
    _file = open("record/" + file_name + ".txt", "a", encoding='utf-8')
    for name in list_name:
        _file.writelines(",".join([name, lable, "\n"]))
    _file.flush()
    _file.close()


def get_car_id(path):
    # ./S/26/1199/34078_#000000_165707.jpg,1199,
    return path.split('/')[4].split('_')[0]


def get_lable(id):
    return id


def generate_train_test_txt(origin_file):
    _file = open(origin_file, "r")
    _car_id = None
    uri_lists = []
    lable = 0
    while 1:
        data_line = _file.readline().replace("\n", "")
        if not data_line:
            break
        data = data_line.split(",")
        print(data)
        car_id = get_car_id(data[0])
        series_id = data[1]
        if not _car_id:
            _car_id = car_id
            uri_lists.append(data[0])
        else:
            if car_id == _car_id:
                uri_lists.append(data[0])
            else:
                val_uri_lists = []
                test_uri_lists = []
                size = len(uri_lists)
                lable = get_lable(series_id)
                if size > 10:
                    val_size = math.ceil(size * 0.2)
                    for i in range(val_size):
                        val = uri_lists.pop(i + 1)
                        val_uri_lists.append(val)
                        val = uri_lists.pop(i + 2)
                        test_uri_lists.append(val)

                list2file(uri_lists, 'train.txt', lable)
                list2file(val_uri_lists, 'val.txt', lable)
                list2file(test_uri_lists, 'test.txt', lable)
                _car_id = car_id
                uri_lists = [data[0]]
    if uri_lists:
        list2file(uri_lists, 'train.txt', lable)
    _file.close()


if __name__ == '__main__':
    list_nam = []
    listdir("../record/images/A/", list_nam)
    list2file(list_nam)
