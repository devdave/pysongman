import sys

import pysongman
from pysongman.views.config.debug import ConfigDebugWindow

from pybass3.bass_stream import BassStream
from pybass3.bass_module import Bass

if pysongman.USE_PYSIDE is True:
    from PySide2 import QtCore, QtWidgets
    from PySide2.QtCore import Qt


class ConfigDebugController(QtCore.QObject):

    view: ConfigDebugWindow

    def __init__(self):
        super(ConfigDebugController, self).__init__()
        self.view = ConfigDebugWindow()
        self.setup_connections()

    def setup_connections(self):

        self.view.update_button.clicked.connect(self.do_update)


    def do_update(self):
        self.view.open_handles.setText(str(len(BassStream.DEBUG_OPEN_HANDLES)))
        self.view.bass_cpu_usage.setText(str(Bass.GetCPU()))
        self.view.widget_count.setText(str(len(pysongman.App.allWidgets())))
        self.view.window_count.setText(str(len(pysongman.App.topLevelWidgets())))
        self.view.playlist_size.setText(str(len(pysongman.playlist)))
