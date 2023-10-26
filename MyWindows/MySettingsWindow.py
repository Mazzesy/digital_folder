from PyQt5.QtWidgets import QDialog, QListWidget, QFrame, QComboBox, QFileDialog, QPushButton, QVBoxLayout
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5 import uic
from pathlib import Path
from MyFunctions import MyConfigFileParser
import fnmatch
import os

from MyWidgets import MyLineEdit

basedir = Path(__file__).parent.parent.absolute()


class MySettingsWindow(QDialog):

    def __init__(self, path_config):
        super().__init__()
        # load ui file
        ui_path = basedir / "gui" / "SettingsWindow.ui"
        uic.loadUi(ui_path, self)

        # define variables
        self.saving_folder_changed = False

        # load data from config file
        # create instance of config file parser
        self.config_parser = MyConfigFileParser()
        # load layout data
        self.layout_folder = self.config_parser.load_config_file("layout_folder", "BASIC", path_config)  # config file
        self.layout_folder = str(Path(self.layout_folder).absolute())
        layouts = [file for file in os.listdir(self.layout_folder) if fnmatch.fnmatch(file, '*.html')]
        self.selected_layout = self.config_parser.load_config_file("layout", "BASIC", path_config)  # config file
        self.layout_file = str(
            Path(self.layout_folder).joinpath(f"{self.selected_layout}.html")
        )
        self.layout_options = [os.path.splitext(os.path.basename(x))[0] for x in layouts]
        # load saving data
        self.saving_folder = self.config_parser.load_config_file("saving_folder", "BASIC", path_config)  # config file
        self.saving_folder = Path(self.saving_folder).absolute()
        # define widgets
        # table of contents
        self.toc = self.findChild(QListWidget, "listWidget_toc")
        features = ["Presentation", "Save"]
        self.toc.addItems(features)
        self.toc.itemClicked.connect(self.on_item_clicked)
        initial_item = self.toc.item(0)  # Choose the initial item by index
        self.toc.setCurrentItem(initial_item)

        # frame for presentation
        self.frame_presentation = self.findChild(QFrame, "frame_presentation")
        self.comboBox_layout_options = self.findChild(QComboBox, "comboBox_layout_options")
        self.comboBox_layout_options.addItems(self.layout_options)
        self.comboBox_layout_options.setCurrentText(self.selected_layout)
        self.comboBox_layout_options.currentTextChanged.connect(self.change_layout)
        self.pushButton_preview = self.findChild(QPushButton, "pushButton_preview")
        self.pushButton_preview.clicked.connect(self.preview_layout)
        self.pushButton_change_folder_layout = self.findChild(QPushButton, "pushButton_change_folder_layout")
        self.pushButton_change_folder_layout.clicked.connect(self.change_layout_folder)

        # frame for saving
        self.frame_savings = self.findChild(QFrame, "frame_saving")
        self.frame_savings.hide()
        self.lineEdit_path = self.findChild(MyLineEdit, "lineEdit_path")
        self.lineEdit_path.setText(self.saving_folder.name)
        # signal that line edit is entered
        self.lineEdit_path.lineEdit_entered.connect(self.to_absolute_path)
        self.pushButton_change_path = self.findChild(QPushButton, "pushButton_change_path")
        self.pushButton_change_path.clicked.connect(self.change_saving_folder)

        # buttons
        self.pushButton_save = self.findChild(QPushButton, "pushButton_save")
        self.pushButton_save.clicked.connect(self.save_settings)
        self.pushButton_cancel = self.findChild(QPushButton, "pushButton_cancel")
        self.pushButton_cancel.clicked.connect(self.reject)

    def to_absolute_path(self):
        self.lineEdit_path.setText(str(self.saving_folder))

    def on_item_clicked(self, item):
        if item.text() == "Save":
            self.frame_presentation.hide()
            self.frame_savings.show()
        elif item.text() == "Presentation":
            self.frame_savings.hide()
            self.frame_presentation.show()
        else:
            raise ValueError(f"Unknown item: {item.text()}")

    def change_layout(self, text):
        self.selected_layout = text
        self.layout_file = str(
            Path(self.layout_folder).joinpath(f"{self.selected_layout}.html")
        )

    def change_layout_folder(self):
        # open file dialog
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly, True)
        dialog.setDirectory(self.layout_folder)
        if dialog.exec_():
            self.layout_folder = dialog.selectedFiles()[0]
            self.layout_options = [os.path.splitext(os.path.basename(x))[0] for x in os.listdir(self.layout_folder)
                                   if fnmatch.fnmatch(x, '*.html')]
            self.comboBox_layout_options.clear()
            self.comboBox_layout_options.addItems(self.layout_options)
            self.comboBox_layout_options.setCurrentText(self.selected_layout)
            self.layout_file = str(Path(self.layout_folder).joinpath(f"{self.selected_layout}.html"))

    def save_settings(self):
        # save layout data
        self.config_parser.write_config_file("layout", self.selected_layout, "BASIC", "config.ini")
        self.config_parser.write_config_file("layout_folder", self.layout_folder, "BASIC", "config.ini")
        # ave saving data
        self.config_parser.write_config_file("saving_folder", str(self.saving_folder), "BASIC", "config.ini")
        self.accept()

    def preview_layout(self):
        dialog_preview = QDialog()
        layout = QVBoxLayout()
        webview = QWebEngineView()
        webview.load(QUrl.fromLocalFile(self.layout_file))
        layout.addWidget(webview)
        dialog_preview.setLayout(layout)
        dialog_preview.setWindowTitle("Preview")
        dialog_preview.resize(800, 600)
        dialog_preview.exec_()

    def change_saving_folder(self):
        # open file dialog
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly, True)
        dialog.setDirectory(str(self.saving_folder))
        if dialog.exec_():
            self.saving_folder = dialog.selectedFiles()[0]
            self.lineEdit_path.setText(self.saving_folder)
            self.saving_folder_changed = True
