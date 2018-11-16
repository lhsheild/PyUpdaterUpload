from PyQt5.QtCore import *
import json
import os


class CheckInfoHelper(QThread):
    signal_get_info = pyqtSignal(tuple)
    signal_get_info_fail = pyqtSignal()

    def __init__(self, target_project):
        super().__init__()
        self.size_dic = None
        self.md5_dic = None
        self.target_project = target_project

    def __del__(self):
        self.wait()

    def run(self):
        self.target_project = os.path.abspath(self.target_project)
        target_project_split_list = self.target_project.split('\\')
        target_project_name = target_project_split_list[-1]
        project_size_file = target_project_name + '_size.json'
        project_md5_file = target_project_name + '_md5.json'

        if os.path.exists(project_size_file):
            with open(project_size_file, 'r') as size_file:
                size_json = size_file.read()
                self.size_dic = json.loads(size_json)

        if os.path.exists(project_md5_file):
            with open(project_md5_file, 'r') as md5_file:
                md5_json = md5_file.read()
                self.md5_dic = json.loads(md5_json)

        if self.size_dic is not None and self.md5_dic is not None:
            self.signal_get_info.emit((self.size_dic, self.md5_dic))
        else:
            self.signal_get_info_fail.emit()
