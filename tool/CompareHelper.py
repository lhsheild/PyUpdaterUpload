from PyQt5.QtCore import *
import os
import hashlib
import json


def get_dir_size(folder):
    size = 0
    for root, dirs, files in os.walk(folder):
        size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
    return size


class GetSizeHelper(object):
    def __init__(self):
        super().__init__()
        self.size_list = []

    def __del__(self):
        self.size_list = None

    def get_size(self, path):
        file_list = os.listdir(path)
        for filename in file_list:
            temp_path = os.path.join(path, filename)
            if os .path.isdir(temp_path):
                self.get_size(temp_path)
            elif os.path.isfile(temp_path):
                file_size = os.path.getsize(temp_path)
                self.size_list.append(file_size)
        return sum(self.size_list)


class FullCheckHelper(QThread):
    signal_get_size = pyqtSignal(str)
    signal_get_md5 = pyqtSignal(str)
    signal_get_full = pyqtSignal()

    def __init__(self, target_folder):
        super().__init__()
        self.target_project = target_folder
        self.project_name = self.target_project.split('/')[-1]
        self.size_dic = {}
        self.md5_dic = {}

    def __del__(self):
        self.size_dic = None
        self.md5_dic = None
        self.wait()

    def run(self):
        for root, dirs, files in os.walk(self.target_project):
            for dir_name in dirs:
                folder = os.path.join(root, dir_name)
                folder = os.path.abspath(folder)
                folder_relative_path = folder.split(self.project_name)[-1]
                # print(folder_relative_path)
                size = get_dir_size(folder)
                self.size_dic[folder] = size
                self.signal_get_size.emit(folder_relative_path)

            for file_name in files:
                file = os.path.join(root, file_name)
                file = os.path.abspath(file)
                file_relative_path = file.split(self.project_name)[-1]
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
                self.md5_dic[file] = md5_value
                self.signal_get_md5.emit(file_relative_path)
        size_json = json.dumps(self.size_dic)
        md5_json = json.dumps(self.md5_dic)
        with open((self.project_name + '_size.json'), 'w') as size_file:
            size_file.write(size_json)
        with open((self.project_name + '_md5.json'), 'w') as md5_file:
            md5_file.write(md5_json)
        self.signal_get_full.emit()


class UpdateCheckHelper(QThread):
    signal_get_changed_info = pyqtSignal(dict)
    signal_cal_folder_size = pyqtSignal(str)
    signal_get_new_folder_size = pyqtSignal(dict)
    signal_cal_file_md5 = pyqtSignal(str)
    signal_get_new_md5 = pyqtSignal(dict)

    def __init__(self, target_folder, size_dic, md5_dic):
        super().__init__()
        self.target_project = target_folder
        self.project_name = self.target_project.split('/')[-1]
        print(self.project_name)
        self.size_dic = size_dic
        self.md5_dic = md5_dic
        self.get_size_helper = GetSizeHelper()
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
        for root, dirs, files in os.walk(self.target_project):
            for dir_name in dirs:
                folder = os.path.join(root, dir_name)
                folder = os.path.abspath(folder)
                folder_relative_path = folder.split(self.project_name)[-1]
                size = get_dir_size(folder)
                self.signal_cal_folder_size.emit(folder_relative_path)
                self.new_size_dic[folder] = size
                if folder not in self.size_dic.keys():
                    self.changed_folder_list.append(folder)
                elif self.size_dic[folder] != size:
                    self.changed_folder_list.append(folder)
        self.changed_folder_list.append(self.target_project)
        self.signal_get_new_folder_size.emit(self.new_size_dic)

        self.new_md5_dic = self.md5_dic
        for i in self.changed_folder_list:
            # print(i)
            file_list = os.listdir(i)
            for file in file_list:
                file = os.path.join(i, file)
                file = os.path.abspath(file)
                if os.path.isfile(file):
                    file_split_list = file.split(self.project_name)
                    file_relative_path = file_split_list[-1]
                    md5 = hashlib.md5()
                    block_size = 2 ** 20
                    with open(file, 'rb') as f:
                        while True:
                            data = f.read(block_size)
                            if not data:
                                break
                            md5.update(data)
                    md5_value = md5.hexdigest()
                    self.signal_cal_file_md5.emit(file_relative_path)
                    if file not in self.md5_dic.keys():
                        self.update_dic[file] = md5_value
                        self.new_md5_dic[file] = md5_value
                    elif self.md5_dic[file] != md5_value:
                        self.update_dic[file] = md5_value
                        self.new_md5_dic[file] = md5_value
        self.signal_get_new_md5.emit(self.new_md5_dic)
        update_info_json = json.dumps(self.update_dic)
        if len(self.update_dic) > 0:
            with open((self.project_name + '_update.json'), 'w') as update_file:
                update_file.write(update_info_json)
        self.signal_get_changed_info.emit(self.update_dic)