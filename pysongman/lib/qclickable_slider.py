"""
    Sourced from https://stackoverflow.com/questions/52689047/moving-qslider-to-mouse-click-position

"""
import logging

import PySide2
from PySide2 import QtWidgets
from PySide2 import QtCore

log = logging.getLogger(__name__)

class QClickableSlider(QtWidgets.QSlider):

    progress_changed = QtCore.Signal(int)

    def mousePressEvent(self, ev:PySide2.QtGui.QMouseEvent) -> None:
        super(QClickableSlider, self).mousePressEvent(ev)
        if ev.button() == QtCore.Qt.LeftButton:
            ev.accept()
            # val = self.pixelPosToRangeValue(ev.pos())
            x = ev.pos().x()
            value = (self.maximum() - self.minimum()) * x / self.width() + self.minimum()

            log.debug("QClickableSlider clicked, val is %s", value)
            self.progress_changed.emit(value)
            self.setValue(value)

    # I feel like this is the better mechanism for getting the right value
    # but i don't know enough about QT to know why this kept returning 0
    # def pixelPosToRangeValue(self, pos):
    #     opt = QtWidgets.QStyleOptionSlider()
    #     self.initStyleOption(opt)
    #     gr = self.style().subControlRect(
    #         QtWidgets.QStyle.CC_Slider,
    #         opt,
    #         QtWidgets.QStyle.SC_SliderGroove,
    #         self)
    #     sr = self.style().subControlRect(
    #         QtWidgets.QStyle.CC_Slider,
    #         opt,
    #         QtWidgets.QStyle.SC_SliderHandle,
    #         self)
    #
    #     if self.orientation() == QtCore.Qt.Horizontal:
    #         sliderLength = sr.width()
    #         sliderMin = gr.x()
    #         sliderMax = gr.right() - sliderLength + 1
    #     else:
    #         sliderLength = sr.height()
    #         sliderMin = gr.y()
    #         sliderMax = gr.bottom() - sliderLength + 1
    #
    #     pr = pos - sr.center() + sr.topLeft()
    #     p = pr.x() if self.orientation() == QtCore.Qt.Horizontal else pr.y()
    #     return QtWidgets.QStyle.sliderPositionFromValue(
    #         self.minimum(),
    #         self.maximum(),
    #         p - sliderMin,
    #         sliderMax - sliderMin,
    #         opt.upsideDown)