from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        center_widget = QWidget()
        self.setCentralWidget(center_widget)

        self.quit_button = self.quit_button_init()  # 退出按钮
        self.check_button = self.check_button_init()  # 检查按钮
        self.upload_button = self.upload_button_init()  # 上传按钮
        self.tips_label = self.tips_label_init()  # 提示标签
        self.progress_bar = self.progressbar_init()  # 进度条

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.check_button)
        button_layout.addWidget(self.upload_button)

        tips_layout = QVBoxLayout()
        tips_layout.addWidget(self.tips_label, 0, Qt.AlignLeft)
        tips_layout.addWidget(self.progress_bar, 0)

        bottom_layout = QHBoxLayout()
        bottom_layout.addLayout(tips_layout)
        bottom_layout.addWidget(self.quit_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(button_layout, 1)
        main_layout.addLayout(bottom_layout, 1)

        center_widget.setLayout(main_layout)
        center_widget.show()

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.drawPixmap(0, 0, 1280, 720, QPixmap(r"D:\Project\PythonProjects\PyUpdaterUpload\resource\世界地图.jpg"))
        painter.end()

    def quit_button_init(self):
        quit_icon = QIcon(r'D:\Project\PythonProjects\PyUpdaterUpload\resource\00007881.png')
        quit_button = QPushButton(self)
        quit_button.setIcon(quit_icon)
        quit_button.setIconSize(QSize(136, 136))
        quit_button.setFixedSize(136, 136)
        quit_button.setStyleSheet(
            "QPushButton{color:black;background-color:transparent;border:none} QPushButton:hover{"
            "background-color:#888888;border:none}")
        quit_button.clicked.connect(lambda: exit(0))
        return quit_button

    def check_button_init(self):
        check_button = QPushButton(self)
        check_icon = QIcon(r'resource\00007BF8.png')
        check_button.setIcon(check_icon)
        check_button.setIconSize(QSize(256, 256))
        check_button.setFixedSize(256, 256)
        check_button.setStyleSheet(
            "QPushButton{color:black;background-color:transparent;} QPushButton:hover{background-color:#888888}")
        check_button.setEnabled(True)
        return check_button

    def upload_button_init(self):
        upload_button = QPushButton(self)
        upload_icon = QIcon(r'D:\Project\PythonProjects\PyUpdaterUpload\resource\Q版.png')
        upload_button.setIcon(upload_icon)
        upload_button.setIconSize(QSize(256, 256))
        upload_button.setFixedSize(256, 256)
        upload_button.setStyleSheet(
            "QPushButton{color:black;background-color:transparent;} QPushButton:hover{background-color:#888888}")
        upload_button.setEnabled(False)
        return upload_button

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
        tips_label.setFixedSize(800, 30)
        return tips_label

    def progressbar_init(self):
        progressbar = QProgressBar(self)
        progressbar.setAlignment(Qt.AlignCenter)
        progressbar.setFixedSize(800, 30)
        # progressbar.setVisible(False)
        return progressbar
