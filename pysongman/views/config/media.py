from pysongman import USE_PYSIDE
from pysongman.tables.parent_dir import ParentTableBridge

if USE_PYSIDE is True:
    from PySide2 import QtWidgets, QtCore
    from PySide2.QtCore import Qt



class MediaConfigWidget(QtWidgets.QWidget):

    def __init__(self, optional_title=None):
        super(MediaConfigWidget, self).__init__()
        self.optional_title = optional_title
        self.setupUI()

    def setupUI(self):

        if self.optional_title is None:
            self.setWindowTitle("Media configuration")
        else:
            self.setWindowTitle(self.optional_title)

        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        if self.optional_title is None:
            groupbox = QtWidgets.QGroupBox("Watch folder settings")
        else:
            groupbox = QtWidgets.QGroupBox(self.optional_title)

        layout.addWidget(groupbox)

        vbox = QtWidgets.QVBoxLayout()
        vbox.setAlignment(Qt.AlignTop)

        groupbox.setLayout(vbox)

        label = QtWidgets.QLabel("New media found in the following folders will automatically be added to the library:")
        label.setWordWrap(True)
        vbox.addWidget(label)

        self.table = QtWidgets.QTableView()
        self.model = ParentTableBridge()

        self.table.setModel(self.model)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
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
        vbox.addStretch()