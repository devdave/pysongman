
from pysongman.tables.parent_dir import ParentTableBridge

from pysongman.lib.qtd import QtCore, Qt, QtWidgets,QtGui



class MediaConfigWidget(QtWidgets.QWidget):

    def __init__(self, parent_table):
        super(MediaConfigWidget, self).__init__()
        self.parent_table = parent_table
        self.setup_ui()

    def setup_ui(self):

        self.setWindowTitle("Media configuration")

        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        groupbox = QtWidgets.QGroupBox("Watch folder settings")

        layout.addWidget(groupbox)

        vbox = QtWidgets.QVBoxLayout()
        vbox.setAlignment(Qt.AlignTop)

        groupbox.setLayout(vbox)

        label = QtWidgets.QLabel("New media found in the following folders will automatically be added to the library:")
        label.setWordWrap(True)
        vbox.addWidget(label)

        self.table = QtWidgets.QTableView()
        self.model = self.parent_table

        self.table.setModel(self.model)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.table.verticalHeader().hide()
        self.table.setColumnHidden(0, True)
        self.table.setMaximumHeight(150)
        self.table.setMaximumWidth(300)

        vbox.addWidget(self.table)

        action_layout = QtWidgets.QHBoxLayout()

        self.add_folder = QtWidgets.QPushButton("Add folder...")
        self.edit_folder = QtWidgets.QPushButton("Edit selected")
        self.remove_folder = QtWidgets.QPushButton("Remove selected")

        action_layout.addWidget(self.add_folder)
        action_layout.addWidget(self.edit_folder)
        action_layout.addWidget(self.remove_folder)

        vbox.addLayout(action_layout)

        self.scan_media = QtWidgets.QPushButton("Scan folders")
        self.scan_status = QtWidgets.QLabel()

        scan_layout = QtWidgets.QHBoxLayout()
        scan_layout.addWidget(self.scan_media)
        scan_layout.addWidget(self.scan_status)

        vbox.addLayout(scan_layout)

        vbox.addStretch()

