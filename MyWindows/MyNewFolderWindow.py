from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QWidget
from PyQt5 import uic
from pathlib import Path

basedir = Path(__file__).parent.parent.absolute()

class MyNewFolderWindow(QDialog):

    def __init__(self):
        super(MyNewFolderWindow, self).__init__()
        ui_path = basedir / "gui" / "NewFolderWindow.ui"
        uic.loadUi(ui_path, self)

        self.project_name = ""
        self.register_names = []

        self.pushButton_reject = self.findChild(QPushButton, "pushButton_reject")
        self.pushButton_reject.clicked.connect(self.reject)

        self.pushButton_create_project = self.findChild(QPushButton, "pushButton_create_project")
        self.pushButton_create_project.clicked.connect(self.create_project)

        self.lineEdit_project_name = self.findChild(QLineEdit, "lineEdit_project_name")

        self.widget_register = self.findChild(QWidget, "widget_register")
        self.widget_register_layout = self.widget_register.layout()
        first_line_edit = self.findChild(QLineEdit, "lineEdit_register_names")

        self.line_edits = [first_line_edit]
        self.line_edits[-1].textChanged.connect(self.add_line_edit)

    def create_project(self):
        self.project_name = self.lineEdit_project_name.text()
        self.register_names = [lineEdit.text() for lineEdit in self.line_edits if lineEdit.text() != ""]
        self.accept()

    def add_line_edit(self, text):
        # This slot will be called when text is entered or modified
        if text and self.sender() == self.line_edits[-1]:
            new_line_edit = QLineEdit(self)
            self.line_edits.append(new_line_edit)
            self.widget_register_layout.addWidget(new_line_edit)
            new_line_edit.textChanged.connect(self.add_line_edit)
        elif not text and len(self.line_edits) > 1:
            # Remove the last QLineEdit if the current one is empty and there's more than one QLineEdit
            # get current QLineEdit
            current_widget = self.focusWidget()
            if current_widget == self.line_edits[-2]:
                last_line_edit = self.line_edits.pop()
                last_line_edit.deleteLater()
            else:
                # if the current widget is not the last QLineEdit, then only delete the current QLineEdit
                current_widget.deleteLater()
                self.line_edits.remove(current_widget)
            self.line_edits[-1].textChanged.connect(self.add_line_edit)
