from pysongman import USE_PYSIDE

if USE_PYSIDE is True:
    from PySide2 import QtCore, QtWidgets
    from PySide2.QtWidgets import QLabel
    from PySide2.QtCore import Qt


class ConfigDebugWindow(QtWidgets.QWidget):

    update_button: QtWidgets.QPushButton
    open_handles: QLabel
    bass_cpu_usage: QLabel
    widget_count: QLabel
    window_count: QLabel
    playlist_size: QLabel

    def __init__(self):
        super(ConfigDebugWindow, self).__init__()
        self.setup_ui()

    def setup_ui(self):
        form = QtWidgets.QFormLayout(self)

        self.update_button = QtWidgets.QPushButton("Update")
        self.open_handles = QLabel("-1")
        self.bass_cpu_usage = QLabel("-1%")
        self.widget_count = QLabel("-1") # Application.allWidgets
        self.window_count = QLabel("-1") # Application.topLevelWidgets
        self.playlist_size = QLabel("-1")

        form.addRow("Refresh", self.update_button)
        form.addRow("Open handles", self.open_handles)
        form.addRow("BASS CPU %", self.bass_cpu_usage)
        form.addRow("Widget #", self.widget_count)
        form.addRow("Window #", self.window_count)
        form.addRow("Sizeof playlist", self.playlist_size)



