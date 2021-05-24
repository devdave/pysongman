import logging
import pathlib

from pysongman.models import get_db
from pysongman.models.parent_dir import ParentDir as ParentDirModel
from pysongman.tables.parent_dir import ParentTableBridge

from pysongman.views.config.media import MediaConfigWidget

from pysongman.lib.qtd import QtCore, QtWidgets, QFileDialog


log = logging.getLogger(__name__)


class ConfigMediaController(QtCore.QObject):
    def __init__(self, optional_title=None):
        super(ConfigMediaController, self).__init__()

        self.optional_title = optional_title
        self.table_model = ParentTableBridge()
        self.view = MediaConfigWidget(self.table_model)
        self.make_connections()

    def make_connections(self):
        self.view.add_folder.clicked.connect(self.on_click_add_folder)
        self.view.edit_folder.clicked.connect(self.on_click_edit_folder)
        self.view.remove_folder.clicked.connect(self.on_click_remove_folder)
        pass

    def on_click_add_folder(self):
        user_dir = pathlib.Path.home()
        log.debug("Add Folder")
        result = QFileDialog.getExistingDirectory(self.view, "Select music directory", user_dir.as_posix())
        if result and result.strip() != "":
            log.debug("User wishes to add %s to media library watch list", result)
            conn = get_db()
            record = ParentDirModel()
            record.path = pathlib.Path(result).as_posix()
            conn.s.add(record)
            conn.s.commit()

            self.view.table.model().beginResetModel()
            self.view.table.model().endResetModel()





    def on_click_edit_folder(self):
        log.debug("Edit Folder")

    def on_click_remove_folder(self):
        row_si = self.view.table.selectionModel().selectedIndexes()[0]
        row_num = self.view.table.selectionModel().selectedIndexes()[0].row()
        if row_num:
            row_idx = self.table_model.index(row_num,0)
            record_num = self.table_model.itemData(row_idx)[0]
            ParentDirModel.query.filter(ParentDirModel.id == record_num).delete()
            log.debug("Removed %s", record_num)
            self.view.table.model().beginResetModel()
            self.view.table.model().endResetModel()


    def show(self):
        self.view.show()

    def hide(self):
        self.view.hide()

    def activate(self):
        self.view.activateWindow()