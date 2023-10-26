from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import pyqtSignal


class MyLineEdit(QLineEdit):

    lineEdit_entered = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def focusInEvent(self, event):
        # This method is called when the QLineEdit receives focus
        self.lineEdit_entered.emit()
