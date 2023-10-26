from MyWindows import MyMainWindow
from PyQt5.QtWidgets import QApplication
import sys


def except_hook(cls, exception, traceback):
    """function to log unhandled exceptions in PyCharm"""
    sys.__excepthook__(cls, exception, traceback)

def main():
    app = QApplication(sys.argv)
    sys.excepthook = except_hook
    window = MyMainWindow()
    # set full size
    window.showMaximized()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
