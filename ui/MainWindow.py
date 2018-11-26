from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from tool import CheckHelper, CompareHelper, FTPHelper
from image_qrc import *

import zipfile
import os
import json
import time
import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon(':/resource/f.png'))
        self.setWindowTitle('三维平台更新包生成程序')
        center_widget = QWidget()
        self.setCentralWidget(center_widget)

        self.quit_button = self.quit_button_init()  # 退出按钮
        self.check_button = self.check_button_init()  # 检查按钮
        self.tips_label = self.tips_label_init()  # 提示标签
        self.progress_bar = self.progressbar_init()  # 进度条

        button_layout = QHBoxLayout(self)
        button_layout.addWidget(self.check_button, 0, Qt.AlignCenter)
        button_layout.addWidget(self.quit_button, 0, Qt.AlignCenter)

        # tips_layout = QVBoxLayout()
        # tips_layout.addWidget(self.tips_label, 0, Qt.AlignLeft)
        # tips_layout.addWidget(self.progress_bar, 0)

        bottom_layout = QVBoxLayout(self)
        bottom_layout.addWidget(self.tips_label, 0, Qt.AlignCenter)
        bottom_layout.addWidget(self.progress_bar, 0, Qt.AlignCenter)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(button_layout)
        main_layout.addSpacerItem(QSpacerItem(1280, 5))
        main_layout.addLayout(bottom_layout)

        center_widget.setLayout(main_layout)
        center_widget.show()

        '''临时变量'''
        self.project_path = None
        self.size_dic = None
        self.md5_dic = None
        self.do_compare = False

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.drawPixmap(0, 0, 1280, 960, QPixmap(':/resource/d.jpg'))
        painter.end()

    def quit_button_init(self):
        quit_icon = QIcon(':/resource/b.png')
        quit_button = QPushButton(self)
        quit_button.setIcon(quit_icon)
        quit_button.setIconSize(QSize(256, 256))
        quit_button.setFixedSize(256, 256)
        quit_button.setStyleSheet(
            "QPushButton{color:black;background-color:transparent;border:none} QPushButton:hover{"
            "background-color:#888888;border:none}")
        quit_button.clicked.connect(lambda: sys.exit(0))
        return quit_button

    def check_button_init(self):
        check_button = QPushButton(self)
        check_icon = QIcon(':/resource/a.png')
        check_button.setIcon(check_icon)
        check_button.setIconSize(QSize(256, 256))
        check_button.setFixedSize(256, 256)
        check_button.setStyleSheet(
            "QPushButton{color:black;background-color:transparent;} QPushButton:hover{background-color:#888888}")
        check_button.setEnabled(True)
        check_button.clicked.connect(lambda: self.select_ckeck_folder())
        check_button.setObjectName('check_button')
        return check_button

    def tips_label_init(self):
        tips_label = QLabel(self)
        tips_label.setAlignment(Qt.AlignCenter)
        tips_label.setStyleSheet('QLabel{color:white}')
        tips_font = QFont()
        tips_font.setFamily("微软雅黑")
        tips_font.setPointSize(16)
        tips_font.setBold(False)
        tips_font.setItalic(False)
        tips_font.setWeight(50)
        tips_label.setFont(tips_font)
        tips_label.setStyleSheet('QLabel{color:white}')
        tips_label.setText('请检测更新文件')
        tips_label.setFixedSize(800, 20)
        tips_label.setObjectName('tips_label')
        return tips_label

    def progressbar_init(self):
        progressbar = QProgressBar(self)
        progressbar.setAlignment(Qt.AlignCenter)
        progressbar.setFixedSize(800, 20)
        progressbar.setVisible(False)
        return progressbar

    def select_ckeck_folder(self):
        selected_folder = QFileDialog.getExistingDirectory(self, '选择文件夹')
        if os.path.exists(selected_folder):
            self.project_path = os.path.abspath(selected_folder)
            self.check_info_backend(self.project_path)

    '''检测是否已有文件信息记录'''

    def check_info_backend(self, project_path):
        self.check_info_helper = CheckHelper.CheckInfoHelper(project_path)
        self.check_info_helper.signal_get_info.connect(self.check_info_success)
        self.check_info_helper.signal_get_info_fail.connect(self.check_info_fail)
        self.check_info_helper.start()

    @pyqtSlot(tuple)
    def check_info_success(self, info_tuplr):
        self.size_dic = info_tuplr[0]
        self.md5_dic = info_tuplr[1]
        self.do_compare = True
        self.compare_info_backend(self.project_path)

    @pyqtSlot()
    def check_info_fail(self):
        self.size_dic = None
        self.md5_dic = None
        self.do_compare = False
        self.cal_info_backend(self.project_path)

    '''计算所有文件信息'''

    def cal_info_backend(self, project_path):
        self.cal_info_helper = CompareHelper.FullCheckHelper(project_path)
        self.cal_info_helper.signal_cal_folder_size.connect(self.cal_folder_size)
        self.cal_info_helper.signal_cal_file_md5.connect(self.cal_file_md5)
        self.cal_info_helper.signal_get_full_info.connect(self.get_full_info)
        self.cal_info_helper.start()

    @pyqtSlot(str)
    def cal_folder_size(self, folder):
        # self.findChild(QLabel, 'tips_label').setText('计算文件夹大小：{}'.format(folder))
        self.tips_label.setText('计算文件夹大小：{}'.format(folder))

    @pyqtSlot(str)
    def cal_file_md5(self, file):
        # self.findChild(QLabel, 'tips_label').setText('计算文件MD5值：{}'.format(file))
        self.tips_label.setText('计算文件MD5值：{}'.format(file))

    @pyqtSlot()
    def get_full_info(self):
        # self.findChild(QLabel, 'tips_label').setText('已生成项目初始信息')
        self.tips_label.setText('已生成项目初始信息')

    '''对比文件信息'''

    def compare_info_backend(self, project_path):
        self.compare_info_helper = CompareHelper.UpdateCheckHelper(project_path, self.size_dic, self.md5_dic)
        self.compare_info_helper.signal_compare_folder_size.connect(self.compare_folder_size)
        self.compare_info_helper.signal_compare_file_md5.connect(self.compare_file_md5)
        self.compare_info_helper.signal_get_new_folder_size.connect(self.get_new_folder_size)
        self.compare_info_helper.signal_get_new_file_md5.connect(self.get_new_file_md5)
        self.compare_info_helper.signal_get_update_info.connect(self.get_update_info)
        self.compare_info_helper.start()

    @pyqtSlot(str)
    def compare_folder_size(self, folder):
        # self.findChild(QLabel, 'tips_label').setText('对比文件夹大小：{}'.format(folder))
        self.tips_label.setText('对比文件夹大小：{}'.format(folder))

    @pyqtSlot(str)
    def compare_file_md5(self, file):
        # self.findChild(QLabel, 'tips_label').setText('对比文件MD5值：{}'.format(file))
        self.tips_label.setText('对比文件MD5值：{}'.format(file))

    @pyqtSlot(tuple)
    def get_new_folder_size(self, size_info):
        project_name = size_info[0]
        size_dic = size_info[1]
        size_json = json.dumps(size_dic)
        with open((project_name + '_size.json'), 'w') as sf:
            sf.write(size_json)

    @pyqtSlot(tuple)
    def get_new_file_md5(self, file_info):
        project_name = file_info[0]
        md5_dic = file_info[1]
        md5_json = json.dumps(md5_dic)
        with open((project_name + '_md5.json'), 'w') as mf:
            mf.write(md5_json)

    @pyqtSlot(tuple)
    def get_update_info(self, update_info):
        project_name = update_info[0]
        index1 = self.project_path.find(project_name)
        project_pre_path = self.project_path[0:index1]
        update_dic = update_info[1]
        time_tick = str(time.time())
        if len(update_dic) > 0:
            with zipfile.ZipFile((project_name + '_' + time_tick + '.zip'), 'w') as zip_file:
                try:
                    for i in update_dic:
                        update_file = os.path.join(project_pre_path, i)
                        update_file = os.path.abspath(update_file)
                        # zip_file.write(update_file)
                        zip_file.write(update_file, i)
                        # self.findChild(QLabel, 'tips_label').setText('压缩文件：{}'.format(update_file))
                        self.tips_label.setText('压缩文件：{}'.format(update_file))
                    zip_file.write(project_name + '_update.json')
                except Exception as e:
                    print(e)

            update_zip = project_name + '_' + time_tick + '.zip'
            try:
                # my_ftp_helper = FTPHelper.MyFtp('172.16.1.156', 21, 'Administrator', '123456')
                # if my_ftp_helper.ftp_login() == 1000:
                #     upload_result = my_ftp_helper.upload_file(update_zip, update_zip)
                #     if upload_result == 1000:
                #         # self.findChild(QLabel, 'tips_label').setText('更新包上传成功：{}'.format(update_zip))
                #         self.tips_label.setText('更新包上传成功：{}'.format(update_zip))
                #     else:
                #         # self.findChild(QLabel, 'tips_label').setText('更新包上传失败，请联系管理员并手动上传更新包')
                #         self.tips_label.setText('更新包上传失败，请联系管理员并手动上传更新包')
                # else:
                #     # self.findChild(QLabel, 'tips_label').setText('服务器链接失败，请联系管理员并手动上传更新包')
                #     self.tips_label.setText('服务器链接失败，请联系管理员并手动上传更新包')
                self.upload_task(update_zip, update_zip)
            except Exception as e:
                print(e)
        else:
            # self.findChild(QLabel, 'tips_label').setText('没有更新内容：{}'.format(project_name))
            self.tips_label.setText('没有更新内容：{}'.format(project_name))

    def upload_task(self, local_file, remote_file):
        self.my_upload_helper = FTPHelper.MyQThreadFTP('192.168.0.133', 21, 'Administrator', 'Gut102015', remote_file,
                                                       local_file, True)
        self.my_upload_helper.signal_local_not_exists.connect(self.upload_local_not_exists)  # 本地文件不存在
        self.my_upload_helper.signal_server_unable.connect(self.upload_server_unable)  # 服务器连接失败
        self.my_upload_helper.signal_server_equal_local.connect(self.upload_server_equal)  # 服务器已有相同文件
        self.my_upload_helper.signal_transfer_fault.connect(self.upload_transfer_fail)  # 上传文件失败
        self.my_upload_helper.signal_upload_process.connect(self.upload_process)  # 上传进度
        self.my_upload_helper.signal_upload_finish.connect(self.upload_finish)  # 上传完成
        self.my_upload_helper.start()

    @pyqtSlot()
    def upload_local_not_exists(self):
        self.tips_label.setText('本地文件不存在!')

    @pyqtSlot(str)
    def upload_server_unable(self, info):
        self.tips_label.setText('服务器连接失败：'.format(info))

    @pyqtSlot()
    def upload_server_equal(self):
        self.tips_label.setText('服务器已存在相同文件')

    @pyqtSlot()
    def upload_transfer_fail(self):
        self.tips_label.setText('文件上传失败')

    @pyqtSlot(int)
    def upload_process(self, process):
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(process)

    @pyqtSlot(str)
    def upload_finish(self, file_name):
        self.progress_bar.setVisible(False)
        self.tips_label.setText('更新包上传成功：'.format(file_name))
