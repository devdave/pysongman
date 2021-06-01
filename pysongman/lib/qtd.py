try:
    from PySide2.QtWidgets import QApplication, QFileDialog, QLabel, QHBoxLayout, QVBoxLayout
    from PySide2.QtWidgets import QLabel, QPushButton, QLineEdit, QFrame, QMenu, QAction
    from PySide2 import QtCore
    from PySide2.QtCore import Qt, Signal, Slot, QObject
    from PySide2 import QtGui, QtWidgets
    import PySide2
    from PySide2.QtGui import QPixmap

    from PySide2.QtWidgets import QAction, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

except ImportError:
    raise NotImplementedError("Missing PyQT5")