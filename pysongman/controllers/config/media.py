from pysongman import USE_PYSIDE

from pysongman.views.config.media import MediaConfigWidget

if USE_PYSIDE is True:
    from PySide2 import QtCore

class ConfigMediaController(QtCore.QObject):
    def __init__(self, optional_title=None):
        self.optional_title = optional_title
        self.view = MediaConfigWidget(optional_title=optional_title)
        self.make_connections()

    def make_connections(self):
        self.view.add_folder.clicked.connect(self.on_click_add_folder)
        self.view.edit_folder.clicked.connect(self.on_click_edit_folder)
        self.view.remove_folder.clicked.connect(self.on_click_remove_folder)
        pass

    def on_click_add_folder(self):
        print("Add Folder", self.optional_title)

    def on_click_edit_folder(self):
        print("Edit folder", self.optional_title)

    def on_click_remove_folder(self):
        print("Remove Folder", self.optional_title)


    def show(self):
        self.view.show()

    def hide(self):
        self.view.hide()

    def activate(self):
        self.view.activateWindow()