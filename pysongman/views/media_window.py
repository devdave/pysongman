from ..lib.qtd import QtCore, Qt, QtWidgets, QMenu, QAction

from ..lib.mdi_window import MDIWindow


class MediaWindow(MDIWindow):

    library_menu: QtWidgets.QMenu
    act_remove_missing: QAction
    act_add_media: QAction
    act_rescan_folders: QAction
    act_media_preferences: QAction

    def setup_ui(self):
        super(MediaWindow, self).setup_ui()
        self.menu_button.setText("Library")

        self.library_menu = QMenu("Library", self)
        self.library_menu.addSeparator()

        self.act_remove_missing = QAction("Remove missing files from Library...")
        self.library_menu.addAction(self.act_remove_missing)

        self.act_add_media = QAction("Add media to Library...")
        self.library_menu.addAction(self.act_add_media)

        self.act_rescan_folders = QAction("Rescan Watch Folders (in background)")
        self.library_menu.addAction(self.act_rescan_folders)

        self.act_media_preferences = QAction("Media Library Preferences")
        self.library_menu.addAction(self.act_media_preferences)

        self.menu_button.setMenu(self.library_menu)










