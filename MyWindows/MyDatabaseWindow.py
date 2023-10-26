from PyQt5.QtWidgets import QDialog, QPushButton, QLineEdit, QListWidget, QTreeView, QInputDialog, QMessageBox
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5 import uic
from pathlib import Path


basedir = Path(__file__).parent.parent.absolute()


class MyDatabaseWindow(QDialog):
    db_changed = pyqtSignal()

    def __init__(self, database):
        super(MyDatabaseWindow, self).__init__()
        ui_path = basedir / "gui" / "DatabaseWindow.ui"
        uic.loadUi(ui_path, self)
        self.database = database
        self.folder_name = ""
        self.folder_names = self.database.get_folder_names()
        self.folder_names = [item[0] for item in self.folder_names]

        self.listWidget_folders = self.findChild(QListWidget, "listWidget_folders")
        self.listWidget_folders.itemClicked.connect(self.show_structure)
        self.listWidget_folders.addItems(self.folder_names)
        self.listWidget_folders.doubleClicked.connect(self.load_folder)

        self.treeView_folder_structure = self.findChild(QTreeView, "treeView_folder_structure")
        self.model = QStandardItemModel()
        self.treeView_folder_structure.setModel(self.model)

        self.pushButton_load_folder = self.findChild(QPushButton, "pushButton_load_folder")
        self.pushButton_load_folder.clicked.connect(self.load_folder)

        self.pushButton_cancel = self.findChild(QPushButton, "pushButton_cancel")
        self.pushButton_cancel.clicked.connect(self.reject)

        self.pushButton_delete_folder = self.findChild(QPushButton, "pushButton_delete_folder")
        self.pushButton_delete_folder.clicked.connect(self.delete_folder)

        self.pushButton_rename_folder = self.findChild(QPushButton, "pushButton_rename_folder")
        self.pushButton_rename_folder.clicked.connect(self.rename_folder)

    def show_structure(self, index):
        self.folder_name = index.text()
        folder_structure = self.database.get_folder_structure(self.folder_name)
        self.model.clear()
        self.rebuild_tree_structure(self.model.invisibleRootItem(), folder_structure)
        self.collapse_all_items()

    def rebuild_tree_structure(self, parent_item, data):
        for item_data in data:
            item = QStandardItem(item_data['text'])
            parent_item.appendRow(item)
            if 'children' in item_data:
                self.rebuild_tree_structure(item, item_data['children'])

    def collapse_all_items(self):
        root_item = self.model.invisibleRootItem()
        for row in range(root_item.rowCount()):
            self.treeView_folder_structure.setExpanded(self.model.index(row, 0), True)

    def load_folder(self):
        if not self.folder_name:
            return
        self.accept()

    def delete_folder(self):
        if not self.folder_name:
            return
        self.database.delete_folder(self.folder_name)
        self.folder_names = self.database.get_folder_names()
        self.folder_names = [item[0] for item in self.folder_names]
        self.listWidget_folders.clear()
        self.listWidget_folders.addItems(self.folder_names)
        self.model.clear()
        self.folder_name = ""
        self.db_changed.emit()

    def rename_folder(self):
        if not self.folder_name:
            return
        new_folder_name, ok = QInputDialog.getText(self, "Rename folder", "New name:",
                                                   QLineEdit.Normal, self.folder_name)
        if ok:
            if new_folder_name in self.folder_names:
                QMessageBox.warning(self, "Rename folder", "Folder name already exists!")
                return
            self.database.rename_folder(self.folder_name, new_folder_name)
            self.database.rename_folder_in_structure(new_folder_name)
            self.folder_names = self.database.get_folder_names()
            self.folder_names = [item[0] for item in self.folder_names]
            self.listWidget_folders.clear()
            self.listWidget_folders.addItems(self.folder_names)
            self.model.clear()
            self.folder_name = ""
            self.db_changed.emit()
