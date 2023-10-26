from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QMenu, QAction, QTreeView, QAbstractItemView
from PyQt5.QtCore import Qt, pyqtSignal, QModelIndex


class MyTreeView(QTreeView):
    item_dropped = pyqtSignal(object, str, str)
    path_to_repair = pyqtSignal(str, QModelIndex)
    register_added = pyqtSignal(QModelIndex)
    entry_deleted = pyqtSignal(QModelIndex)
    folder_deleted = pyqtSignal()
    document_added = pyqtSignal(QModelIndex)
    document_opened = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSelectionMode(self.SingleSelection)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.contextMenu = None

    def dragEnterEvent(self, event) -> None:
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            event.accept()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event) -> None:
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            parent_index = self.indexAt(event.pos())
            self.setCurrentIndex(parent_index)
            event.accept()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        # Handle drop events to add a file name as a sub-entry
        mime_data = event.mimeData()

        if mime_data.hasUrls():
            parent_index = self.indexAt(event.pos())

            if parent_index.isValid():
                parent_item = self.model().itemFromIndex(parent_index)

                if parent_item:
                    for url in mime_data.urls():
                        file_name = url.fileName()
                        file_path = url.path()
                        self.item_dropped.emit(parent_item, file_name, file_path)
        else:
            super().dropEvent(event)

    def contextMenuEvent(self, event):
        self.contextMenu = QMenu(self)

        action_repair_file_path = QAction("Repair path", self)
        action_repair_file_path.triggered.connect(self.repair_path)
        action_change_file_path = QAction("Change path", self)
        action_change_file_path.triggered.connect(self.repair_path)
        action_add_register = QAction("Add register", self)
        action_add_register.triggered.connect(self.add_register)
        action_delete_entry = QAction("Delete entry", self)
        action_delete_entry.triggered.connect(self.delete_entry)
        action_delete_folder = QAction("Close folder", self)
        action_delete_folder.triggered.connect(self.delete_folder)
        action_add_entry = QAction("Add document", self)
        action_add_entry.triggered.connect(self.document_to_add)
        action_open_entry = QAction("Open document", self)
        action_open_entry.triggered.connect(self.open_document)

        index = self.selectionModel().currentIndex()
        if not index.isValid():
            return
        self.contextMenu.addAction(action_add_register)
        item = self.model().itemFromIndex(index)
        # Check if the item has an icon
        icon_check = item.data(Qt.DecorationRole)
        # if it has an icon, add the action to the context menu
        if icon_check is not None:
            self.contextMenu.addAction(action_repair_file_path)
        if item.parent() is not None:
            self.contextMenu.addAction(action_change_file_path)
            self.contextMenu.addAction(action_delete_entry)
            self.contextMenu.addAction(action_add_entry)
            self.contextMenu.addAction(action_open_entry)
        else:
            self.contextMenu.addAction(action_delete_folder)

        self.contextMenu.popup(QCursor.pos())

    def open_document(self):
        index = self.selectionModel().currentIndex()
        item = self.model().itemFromIndex(index)
        text = item.text()
        self.document_opened.emit(text)

    def document_to_add(self):
        index = self.selectionModel().currentIndex()
        self.document_added.emit(index)

    def repair_path(self):
        index = self.selectionModel().currentIndex()
        item = self.model().itemFromIndex(index)
        text = item.text()
        self.path_to_repair.emit(text, index)

    def add_register(self):
        index = self.selectionModel().currentIndex()
        self.register_added.emit(index)

    def delete_entry(self):
        index = self.selectionModel().currentIndex()
        self.entry_deleted.emit(index)

    def delete_folder(self):
        self.folder_deleted.emit()
