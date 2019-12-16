# -*- coding: utf-8 -*-
import os


def listdir(path, list_name):
    """
    遍历path下的所有文件，将文件相对地址存入list_name 返回
    :param path: 将要遍历的路径
    :param list_name: list引用
    :return: 文件相对路径list集合
    """
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            listdir(file_path, list_name)
        else:
            list_name.append(file_path.replace("\\", "/"))
    return list_name


def list2file(list_name, file_name, label):
    """
    将list中的值写入文件
    :param list_name: 集合名称
    :param file_name: 文件名称
    :param label: 该集合所属的标签
    :return: None
    """
    _file = open("record/" + file_name + ".txt", "a", encoding='utf-8')
    for name in list_name:
        _file.writelines(",".join([name, label, "\n"]))
    _file.flush()
    _file.close()


def get_model_id(path):
    return path.split('/')[1]


def get_label_dict():
    """
    读取attributes文件将model_id 与 type 组成dict
    :return: model_id 与 type 的dict
    """
    labels = {}
    label_file = open(r"E:\data\CompCars\data\misc\attributes.txt", "r")
    while 1:
        data_line = label_file.readline().replace("\n", "")
        if not data_line:
            break
        data = data_line.split(" ")
        labels[data[0]] = data[5]
    return labels


def generate_train_val_test_txt(origin_file, target_file, labels):
    _origin_file = open(origin_file, "r")
    _target_file = open(target_file, "a")
    while 1:
        data_line = _origin_file.readline().replace("\n", "")
        if not data_line:
            break
        data = data_line.split(",")
        print(data)
        path = data[0]
        model_id = get_model_id(path)
        label = labels[str(model_id)]
        _target_file.writelines(",".join(["./images/" + path, label, "\n"]))

    _origin_file.close()
    _target_file.close()


def main():
    label_dict = get_label_dict()
    generate_train_val_test_txt(r"E:\data\CompCars\data\train_test_split\verification\verification_train.txt",
                                "../data/val.txt", label_dict)


if __name__ == '__main__':
    main()
