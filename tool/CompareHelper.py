from PyQt5.QtCore import *
import os
import hashlib
import json


def get_dir_size(folder):
    size = 0
    for root, dirs, files in os.walk(folder):
        size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
    return size


class FullCheckHelper(QThread):
    signal_cal_folder_size = pyqtSignal(str)
    signal_cal_file_md5 = pyqtSignal(str)
    signal_get_full_info = pyqtSignal()

    def __init__(self, project_path):
        super().__init__()
        self.project_abspath = os.path.abspath(project_path)
        self.project_name = self.project_abspath.split('\\')[-1]
        self.size_dic = {}
        self.md5_dic = {}

    def __del__(self):
        self.size_dic = None
        self.md5_dic = None
        self.wait()

    def run(self):
        for root, dirs, files in os.walk(self.project_abspath):
            for dir_name in dirs:
                folder = os.path.join(root, dir_name)
                folder = os.path.abspath(folder)
                folder_index1 = folder.find(self.project_name)
                folder_relative_path = folder[folder_index1:]
                # print(folder_relative_path)
                size = get_dir_size(folder)
                self.size_dic[folder_relative_path] = size
                self.signal_cal_folder_size.emit(folder_relative_path)

            for file_name in files:
                file = os.path.join(root, file_name)
                file = os.path.abspath(file)
                file_index1 = file.find(self.project_name)
                file_relative_path = file[file_index1:]
                # print(file_relative_path)
                md5 = hashlib.md5()
                block_size = 2 ** 20
                with open(file, 'rb') as f:
                    while True:
                        data = f.read(block_size)
                        if not data:
                            break
                        md5.update(data)
                md5_value = md5.hexdigest()
                self.md5_dic[file_relative_path] = md5_value
                self.signal_cal_file_md5.emit(file_relative_path)

        size_json = json.dumps(self.size_dic)
        md5_json = json.dumps(self.md5_dic)
        with open((self.project_name + '_size.json'), 'w') as size_file:
            size_file.write(size_json)
        with open((self.project_name + '_md5.json'), 'w') as md5_file:
            md5_file.write(md5_json)
        self.signal_get_full_info.emit()


class UpdateCheckHelper(QThread):
    signal_get_update_info = pyqtSignal(tuple)
    signal_compare_folder_size = pyqtSignal(str)
    signal_get_new_folder_size = pyqtSignal(tuple)
    signal_compare_file_md5 = pyqtSignal(str)
    signal_get_new_file_md5 = pyqtSignal(tuple)

    def __init__(self, project_path, size_dic, md5_dic):
        super().__init__()
        self.project_abspath = os.path.abspath(project_path)
        self.project_name = self.project_abspath.split('\\')[-1]
        self.size_dic = size_dic
        self.md5_dic = md5_dic
        self.changed_folder_list = []
        self.update_dic = {}
        self.new_size_dic = {}
        self.new_md5_dic = {}

    def __del__(self):
        self.changed_folder_list = None
        self.update_dic = None
        self.new_size_dic = None
        self.new_md5_dic = None
        self.wait()

    def run(self):
        for root, dirs, files in os.walk(self.project_abspath):
            for dir_name in dirs:
                folder = os.path.join(root, dir_name)
                folder = os.path.abspath(folder)
                folder_index1 = folder.find(self.project_name)
                folder_relative_path = folder[folder_index1:]
                size = get_dir_size(folder)
                self.signal_compare_folder_size.emit(folder_relative_path)  # 对比文件夹
                self.new_size_dic[folder_relative_path] = size
                if folder_relative_path not in self.size_dic.keys():
                    self.changed_folder_list.append(folder)
                elif self.size_dic[folder_relative_path] != size:
                    self.changed_folder_list.append(folder)
        self.changed_folder_list.append(self.project_abspath)
        self.signal_get_new_folder_size.emit((self.project_name, self.new_size_dic))  # 生成新的文件夹大小信息文件

        self.new_md5_dic = self.md5_dic
        for i in self.changed_folder_list:
            file_list = os.listdir(i)
            for file in file_list:
                file = os.path.join(i, file)
                file = os.path.abspath(file)
                if os.path.isfile(file):
                    file_index1 = file.find(self.project_name)
                    file_relative_path = file[file_index1:]
                    md5 = hashlib.md5()
                    block_size = 2 ** 20
                    with open(file, 'rb') as f:
                        while True:
                            data = f.read(block_size)
                            if not data:
                                break
                            md5.update(data)
                    md5_value = md5.hexdigest()
                    self.signal_compare_file_md5.emit(file_relative_path)  # 对比文件
                    if file_relative_path not in self.md5_dic.keys():
                        self.update_dic[file_relative_path] = md5_value
                        self.new_md5_dic[file_relative_path] = md5_value
                    elif self.md5_dic[file_relative_path] != md5_value:
                        self.update_dic[file_relative_path] = md5_value
                        self.new_md5_dic[file_relative_path] = md5_value
        self.signal_get_new_file_md5.emit((self.project_name, self.new_md5_dic))  # 生成新的文件MD5值信息文件
        update_json = json.dumps(self.update_dic)
        if len(self.update_dic) > 0:
            with open((self.project_name + '_update.json'), 'w') as update_file:
                update_file.write(update_json)
        self.signal_get_update_info.emit((self.project_name, self.update_dic))  # 生成更新文件信息文件
