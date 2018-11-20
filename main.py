from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from ui import MainWindow

import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)

    main_window = MainWindow.MainWindow()
    main_window.setFixedSize(1280, 720)
    main_window.move((app.desktop().screen().width() - main_window.width()) / 2,
                     (app.desktop().screen().height() - main_window.height()) / 2)
    main_window.show()

    sys.exit(app.exec_())