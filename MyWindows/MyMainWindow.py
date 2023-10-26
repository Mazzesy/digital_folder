from PyQt5.QtWidgets import QMainWindow, QPushButton, QDialog, QFileDialog, QInputDialog, QMessageBox, \
    QWidget, QHBoxLayout, QTableView, QHeaderView, QDockWidget, QTabWidget, QStackedWidget
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtCore import QUrl, Qt, QTimer
from PyQt5 import uic
from PyQt5.QAxContainer import QAxWidget
from qtwidgets import Toggle

import os
from pathlib import Path
from datetime import datetime
import win32com.client
import subprocess
import qdarktheme
import shutil

from MyFunctions import MyDatabase, MyConfigFileParser
from MyWindows import MyNewFolderWindow, MyDatabaseWindow, MySettingsWindow
from MyWidgets import MyTreeView, MyWebWidget


def open_office_documents(app, path):
    # Create a new instance of the office application
    app = win32com.client.Dispatch(app)
    # Make the office application visible (optional)
    app.Visible = True
    # Open the office document
    app.Documents.Open(path)

basedir = Path(__file__).parent.parent.absolute()

class MyMainWindow(QMainWindow):

    def __init__(self):
        super(MyMainWindow, self).__init__()
        ui_path = basedir / "gui" / "MainWindow.ui"
        uic.loadUi(ui_path, self)

        # load settings
        self.layout_folder = None
        self.selected_layout = None
        self.layout_file = None
        self.path_to_save_folder = None
        self.path_to_database = None

        self.path_config = "./config.ini"
        if not os.path.exists(self.path_config):
            shutil.copyfile(basedir / "config.ini", self.path_config)
        else:
            print("Config file already exists")
        self.config_parser = MyConfigFileParser()
        self.load_settings()
        qdarktheme.setup_theme("light")

        # set variables
        self.database = MyDatabase(self.path_to_database)
        self.project_files = {}
        self.project_name = ""
        self.register_names = []
        self.missing_files = []
        self.previous_tab_index = 0

        self.dockWidget_toc = self.findChild(QDockWidget, "dockWidget_toc")
        # signal that is emitted when the dock widget is closed
        self.dockWidget_toc.visibilityChanged.connect(self.toc_visibility_changed)

        self.tabWidget_mainwindow = self.findChild(QTabWidget, "tabWidget_mainwindow")
        # find tree view for table of contents
        self.treeView_toc = self.findChild(MyTreeView, "treeView_toc")
        # connect signals
        self.treeView_toc.item_dropped.connect(self.add_sub_entry)
        self.treeView_toc.path_to_repair.connect(self.repair_broken_path)
        self.treeView_toc.register_added.connect(self.add_register)
        self.treeView_toc.entry_deleted.connect(self.delete_entry)
        self.treeView_toc.folder_deleted.connect(self.clear_view)
        self.treeView_toc.document_added.connect(self.add_document)
        self.treeView_toc.document_opened.connect(self.open_document)
        # create model and set it to tree view
        self.model = QStandardItemModel()
        self.treeView_toc.setModel(self.model)
        self.treeView_toc.selectionModel().selectionChanged.connect(self.show_file)
        # find buttons and connect clicked signal
        self.pushButton_load_folder = self.findChild(QPushButton, "pushButton_load_folder")
        self.pushButton_load_folder.clicked.connect(self.show_archive)
        self.pushButton_new_project = self.findChild(QPushButton, "pushButton_new_project")
        self.pushButton_new_project.clicked.connect(self.new_folder)
        self.pushButton_save_folder = self.findChild(QPushButton, "pushButton_save_folder")
        self.pushButton_save_folder.clicked.connect(self.save_folder)
        self.pushButton_clear_view = self.findChild(QPushButton, "pushButton_clear_view")
        self.pushButton_clear_view.clicked.connect(self.clear_view)
        # find stacked widget for displaying files
        self.stackedWidget_main_window = self.findChild(QStackedWidget, "stackedWidget_main_window")
        self.stackedWidget_main_window.setCurrentIndex(0)
        self.widget_web_view = self.findChild(MyWebWidget, "widget_web_view")
        self.axWidget = self.findChild(QAxWidget, "ax_widget")
        # find table view for history
        self.tableView_history = self.findChild(QTableView, "tableView_history")
        self.tableView_history.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # create model and set it to table view
        self.model_history = QStandardItemModel()
        self.tableView_history.setModel(self.model_history)
        # connect double click signal
        self.tableView_history.doubleClicked.connect(self.load_from_history)
        # set history to table view
        self.set_table_view_history()

        # initialize statusbar
        statusbar_widget = QWidget(self)
        statusbar_layout = QHBoxLayout(statusbar_widget)
        statusbar_layout.setContentsMargins(0, 0, 0, 0)
        statusbar_layout.setAlignment(Qt.AlignLeft)  # Align items to the left
        # create status button
        self.button_warning = QPushButton()
        self.button_clear = QPushButton()
        self.button_settings = QPushButton()
        self.button_save = QPushButton()
        self.button_toc_visibility = QPushButton()
        self.toggle_darkmodus = Toggle()
        # set icons to status button
        self.button_warning.setIcon(QIcon(str(basedir / "icons" / "warning.png")))
        self.button_clear.setIcon(QIcon(str(basedir / "icons" / "clear.png")))
        self.button_settings.setIcon(QIcon(str(basedir / "icons" / "settings.png")))
        self.button_save.setIcon(QIcon(str(basedir / "icons" / "save.png")))
        self.button_toc_visibility.setIcon(QIcon(str(basedir / "icons" / "hide.png")))
        # remove border from button
        self.button_warning.setStyleSheet("QPushButton {border: none;}")
        self.button_clear.setStyleSheet("QPushButton {border: none;}")
        self.button_settings.setStyleSheet("QPushButton {border: none;}")
        self.button_save.setStyleSheet("QPushButton {border: none;}")
        self.button_toc_visibility.setStyleSheet("QPushButton {border: none;}")
        # connect clicked signal
        self.button_warning.clicked.connect(self.show_warnings)
        self.button_clear.clicked.connect(self.clear_view)
        self.button_clear.clicked.connect(self.button_warning.hide)
        self.button_settings.clicked.connect(self.show_settings)
        self.button_save.clicked.connect(self.save_folder)
        self.button_toc_visibility.clicked.connect(self.toc_visibility)
        self.toggle_darkmodus.clicked.connect(
            lambda state: qdarktheme.setup_theme() if state else qdarktheme.setup_theme("light"))
        # add tooltips
        self.button_warning.setToolTip("Broken paths")
        self.button_clear.setToolTip("Clear View")
        self.button_settings.setToolTip("Settings")
        self.button_save.setToolTip("Save")
        self.button_toc_visibility.setToolTip("Hide table of contents")
        self.toggle_darkmodus.setToolTip("Dark mode")
        # add button to status bar
        statusbar_layout.addWidget(self.button_warning)
        statusbar_layout.addWidget(self.button_clear)
        statusbar_layout.addWidget(self.button_settings)
        statusbar_layout.addWidget(self.button_save)
        statusbar_layout.addWidget(self.button_toc_visibility)
        statusbar_layout.addWidget(self.toggle_darkmodus)
        # hide button
        self.button_warning.hide()
        # Add the button widget to the status bar
        self.statusbar.addPermanentWidget(statusbar_widget)

    def toc_visibility_changed(self, state):
        if state:
            self.button_toc_visibility.setIcon(QIcon(str(basedir / "icons" / "hide.png")))
        else:
            self.button_toc_visibility.setIcon(QIcon(str(basedir / "icons" / "show.png")))

    def toc_visibility(self):
        if self.dockWidget_toc.isVisible():
            self.dockWidget_toc.hide()
            self.button_toc_visibility.setIcon(QIcon(str(basedir / "icons" / "show.png")))
        else:
            self.dockWidget_toc.show()
            self.button_toc_visibility.setIcon(QIcon(str(basedir / "icons" / "hide.png")))

    def load_settings(self):
        self.layout_folder = self.config_parser.load_config_file("layout_folder", "BASIC", self.path_config)
        self.selected_layout = self.config_parser.load_config_file("layout", "BASIC", self.path_config)
        self.layout_file = Path(self.layout_folder).joinpath(f"{self.selected_layout}.html")
        self.path_to_save_folder = self.config_parser.load_config_file("saving_folder", "BASIC", self.path_config)
        self.path_to_database = str(Path(self.path_to_save_folder).joinpath("database.db").absolute())

    def new_folder(self):
        new_project_window = MyNewFolderWindow()
        new_project_window.exec_()

        if new_project_window.result() == QDialog.Accepted:
            if new_project_window.project_name in self.database.get_all_folder_names():
                QMessageBox.warning(self, "Rename file", "Folder with this name already exists.")
                return
            self.project_name = new_project_window.project_name
            self.register_names = new_project_window.register_names
            self.model.clear()
            self.add_to_treeview(self.project_name, self.register_names)

    def save_folder(self):
        if not self.project_name:
            return

        tree_data = []
        root_item = self.model.invisibleRootItem()
        self.traverse_tree_structure(root_item, tree_data)
        self.database.save_folder_structure(tree_data, self.project_name)
        self.database.save_folder_files(self.project_files, self.project_name)
        self.database.save_folder_register(self.register_names, self.project_name)
        self.database.save_folder_timestamp(self.project_name)
        self.set_table_view_history()
        print("Saved to database")

    def traverse_tree_structure(self, item, data):
        for row in range(item.rowCount()):
            child_item = item.child(row)
            item_data = {'text': child_item.text()}
            if child_item.hasChildren():
                item_data['children'] = []
                self.traverse_tree_structure(child_item, item_data['children'])
            data.append(item_data)

    def show_archive(self):
        database_window = MyDatabaseWindow(self.database)
        database_window.db_changed.connect(self.set_table_view_history)
        database_window.exec_()
        if database_window.result() == QDialog.Accepted:
            folder_name = database_window.folder_name
            self.load_folder(folder_name)

    def load_folder(self, folder_name):
        try:
            folder_structure = self.database.get_folder_structure(folder_name)
            self.register_names = self.database.get_folder_register(folder_name)
            self.project_name = folder_structure[0]['text']
            self.model.clear()
            self.project_files = self.database.get_folder_files(folder_name)
            self.missing_files = self.check_if_file_exists(self.project_files)
            if self.missing_files:
                self.button_warning.setToolTip(f"{len(self.missing_files)} broken paths!")
                self.button_warning.show()
            self.rebuild_tree_structure(self.model.invisibleRootItem(), folder_structure, self.missing_files)
            self.database.save_folder_timestamp(self.project_name)
            self.set_table_view_history()
            self.tabWidget_mainwindow.setCurrentIndex(1)
        except TypeError:
            QMessageBox.warning(self, "Not found", "Folder not found")

    def load_from_history(self, index):
        folder_name = self.model_history.item(index.row()).text()
        self.load_folder(folder_name)

    def rebuild_tree_structure(self, parent_item, data, missing_files):
        for item_data in data:
            if item_data['text'] in missing_files:
                item = QStandardItem(QIcon("./icons/warning.png"), item_data['text'])
            else:
                item = QStandardItem(item_data['text'])
            parent_item.appendRow(item)
            if 'children' in item_data:
                self.rebuild_tree_structure(item, item_data['children'], missing_files)

    def add_to_treeview(self, project_name, register_names):
        parent_item = QStandardItem(project_name)
        self.model.appendRow(parent_item)

        for register_name in register_names:
            register_name = register_name.strip()
            register_item = QStandardItem(register_name)
            parent_item.appendRow(register_item)

    def add_sub_entry(self, parent_item, text, path):
        sub_item = QStandardItem(text)
        parent_item.appendRow(sub_item)
        self.project_files[text] = path

    def show_file(self, selected):
        if not selected.indexes():
            return
        index = selected.indexes()[0]
        text = index.data()
        if path := self.project_files.get(text, None):
            if path.endswith(".pdf"):
                self.stackedWidget_main_window.setCurrentIndex(0)
                self.widget_web_view.load(QUrl.fromLocalFile(path))
            elif path.endswith(".docx") or path.endswith(".doc"):
                self.widget_web_view.setHtml("")
                self.open_office(path, "Word.Application")
            elif path.endswith(".xlsx") or path.endswith(".xls"):
                self.widget_web_view.setHtml("")
                self.open_office(path, "Excel.Application")
            elif path.endswith(".pptx") or path.endswith(".ppt"):
                self.widget_web_view.setHtml("")
                self.open_office(path, "PowerPoint.Application")
            else:
                self.stackedWidget_main_window.setCurrentIndex(0)
                self.widget_web_view.setHtml("File type not supported yet")
        else:
            self.stackedWidget_main_window.setCurrentIndex(0)
            with open(self.layout_file, "r") as file:
                html_content = file.read()
            html_content = html_content.replace("{dynamic_title}", text)
            self.widget_web_view.setHtml(html_content)

    def open_office(self, path, app):
        self.stackedWidget_main_window.setCurrentIndex(1)
        self.axWidget.clear()
        if not self.axWidget.setControl(app):
            return QMessageBox.critical(self, 'Error', f'{app} not found')
        self.axWidget.dynamicCall('SetVisible (bool Visible)', 'false')
        self.axWidget.setProperty('DisplayAlerts', False)
        self.axWidget.setControl(path)
        # adjust size of axWidget
        QTimer.singleShot(5, self.axWidget.updateGeometry)

    @staticmethod
    def check_if_file_exists(project_files):
        return [key for key, value in project_files.items() if not os.path.exists(value)]

    def repair_broken_path(self, text, index):
        if text not in self.project_files:
            return
        broken_path = self.project_files[text]
        start_folder = str(Path(broken_path).parent.absolute())
        if broken_path.endswith(".pdf"):
            file_option = 'pdf(*.pdf)'
        elif broken_path.endswith(".docx") or broken_path.endswith(".doc"):
            file_option = 'word(*.docx *.doc)'
        elif broken_path.endswith(".xlsx") or broken_path.endswith(".xls"):
            file_option = 'excel(*.xlsx *.xls)'
        else:
            file_option = 'all(*.*)'
        path, _ = QFileDialog.getOpenFileName(self, "Search path", start_folder, file_option)
        if path:
            self.reset_path_to_file(path, text, index)

    def reset_path_to_file(self, path, text, index):
        self.project_files[text] = path
        self.widget_web_view.load(QUrl.fromLocalFile(path))
        target_item = self.model.itemFromIndex(index)
        target_item.setText(text)
        target_item.setIcon(QIcon())
        if text in self.missing_files:
            self.missing_files.remove(text)
        self.button_warning.setToolTip(f"{len(self.missing_files)} broken paths!")
        if not self.missing_files:
            self.button_warning.hide()

    def open_document(self, name):
        if not (path := self.project_files.get(name, None)):
            return
        if not os.path.exists(path):
            QMessageBox.warning(self, "Not found", "File not found")
        elif path.endswith(".pdf"):
            # open pdf with default pdf viewer
            subprocess.Popen([path], shell=True)
        elif path.endswith(".docx") or path.endswith(".doc"):
            open_office_documents("Word.Application", path)
        elif path.endswith(".xlsx") or path.endswith(".xls"):
            open_office_documents("Excel.Application", path)
        else:
            QMessageBox.warning(self, "Error", "File type not supported yet")

    def add_document(self, index):
        # get row of index
        row = index.row()
        # get path to document
        path, _ = QFileDialog.getOpenFileName(self, "Add document", "", "all(*.*)")
        if path:
            document_item = QStandardItem(Path(path).name)
            if parent_item := self.model.itemFromIndex(index.parent()):
                parent_item.insertRow(row + 1, document_item)
            else:
                parent_item = self.model.itemFromIndex(index)
                parent_item.insertRow(0, document_item)

            self.project_files[Path(path).name] = path

    def add_register(self, index):
        register_name, _ = QInputDialog.getText(self, "Add register", "Name of register")

        if register_name:
            register_item = QStandardItem(register_name)
            if parent_item := self.model.itemFromIndex(index.parent()):
                parent_item.appendRow(register_item)
            else:
                parent_item = self.model.itemFromIndex(index)
                parent_item.insertRow(0, register_item)

            self.register_names.append(register_name)

    def delete_entry(self, index):
        item = self.model.itemFromIndex(index)
        if item.hasChildren():
            self.delete_register(item, index)
        else:
            self.delete_file(item, index)

    def delete_register(self, item, index):
        if item.hasChildren():
            for row in range(item.rowCount()):
                child_item = item.child(row)
                child_index = child_item.index()
                self.delete_register(child_item, child_index)
        self.delete_file(item, index)

    def delete_file(self, item, index):
        text = item.text()
        if text in self.project_files:
            del self.project_files[text]
        self.model.removeRow(index.row(), index.parent())
        self.treeView_toc.update()

    def clear_view(self):
        self.model.clear()
        self.project_files = {}
        self.project_name = ""
        self.register_names = []
        self.tabWidget_mainwindow.setCurrentIndex(0)
        self.axWidget.clear()
        self.widget_web_view.setHtml("")

    def show_warnings(self):
        if self.missing_files:
            QMessageBox.warning(self, "Warning",
                                "The following documents were not found:\n" + "\n".join(self.missing_files))

    def show_settings(self):
        settings_window = MySettingsWindow(self.path_config)
        settings_window.exec_()

        if settings_window.result() == QDialog.Accepted:
            self.load_settings()
            if settings_window.saving_folder_changed:
                self.database = MyDatabase(self.path_to_database)
                self.set_table_view_history()

    def set_table_view_history(self):
        self.model_history.clear()
        history = self.database.get_folder_history()
        history = sorted(history, key=lambda x: datetime.strptime(x[1], '%Y-%m-%d %H:%M:%S.%f'), reverse=True)

        for document, timestamp in history:
            # create enable item for document name
            name = QStandardItem(document)
            name.setEditable(False)
            # create enable item for date
            timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
            time = QStandardItem(timestamp.strftime("%d.%m.%Y %H:%M"))
            time.setEditable(False)
            # add items to model
            self.model_history.appendRow([name, time])
        # set header and resize columns
        self.model_history.setHorizontalHeaderLabels(['Name', "Date"])
        self.tableView_history.resizeColumnsToContents()
