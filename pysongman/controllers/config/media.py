import logging
import pathlib

import pysongman
from pysongman.models import get_db
from pysongman.models.parent_dir import ParentDir as ParentDirModel
from pysongman.tables.parent_dir import ParentTableBridge

from pysongman.views.config.media import MediaConfigWidget

from pysongman.lib.qtd import QtCore, QtWidgets, QFileDialog, Signal, Slot


log = logging.getLogger(__name__)


class MediaConfigController(QtCore.QObject):
    def __init__(self):
        super(MediaConfigController, self).__init__()

        self.table_model = ParentTableBridge()
        self.view = MediaConfigWidget(self.table_model)
        self.setup_connections()

        self.scan_in_progress = False

    def setup_connections(self):
        self.view.add_folder.clicked.connect(self.do_click_add_folder)
        self.view.edit_folder.clicked.connect(self.do_click_edit_folder)
        self.view.remove_folder.clicked.connect(self.do_click_remove_folder)

        self.view.scan_media.clicked.connect(self.do_scan_request)

    def do_click_add_folder(self):
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

    def do_click_edit_folder(self):
        log.debug("Edit Folder")

    def do_click_remove_folder(self):
        row_si = self.view.table.selectionModel().selectedIndexes()[0]
        row_num = self.view.table.selectionModel().selectedIndexes()[0].row()
        if row_num:
            row_idx = self.table_model.index(row_num,0)
            record_num = self.table_model.itemData(row_idx)[0]
            ParentDirModel.query.filter(ParentDirModel.id == record_num).delete()
            log.debug("Removed %s", record_num)
            self.view.table.model().beginResetModel()
            self.view.table.model().endResetModel()

    def do_scan_request(self):
        if self.scan_in_progress is True:
            QtWidgets.QMessageBox.information(self.view, "Scan in progress", "Background is already running")

        self.scan_in_progress = True

        scanner = pysongman.App.generate_media_scanner_worker() # type: MediaLibScanner
        # Setup signal connects here
        scanner.signals.completed.connect(self.on_media_scan_complete)
        scanner.signals.file_processed.connect(lambda fpath: self.view.scan_status.setText(fpath))

        pysongman.App.execute_media_scanner(scanner)

    @Slot()
    def on_media_scan_complete(self):
        self.scan_in_progress = False

    def show(self):
        self.view.show()

    def hide(self):
        self.view.hide()

    def activate(self):
        self.view.activateWindow()