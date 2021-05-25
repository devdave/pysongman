try:
    from PySide2.QtWidgets import QApplication, QFileDialog, QLabel, QHBoxLayout, QVBoxLayout
    from PySide2.QtWidgets import QLabel, QPushButton, QLineEdit, QFrame
    from PySide2 import QtCore
    from PySide2.QtCore import Qt, Signal, Slot, QObject
    from PySide2 import QtGui, QtWidgets

except ImportError:
    raise NotImplementedError("Missing PyQT5")