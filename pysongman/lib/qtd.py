try:
    from PySide2.QtWidgets import QApplication
    from PySide2 import QtCore
    from PySide2.QtCore import Qt, Signal, Slot
    from PySide2 import QtGui
except ImportError:
    raise NotImplementedError("Missing PyQT5")