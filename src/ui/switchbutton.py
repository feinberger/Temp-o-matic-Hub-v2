"""This module is a custom widget for a toggle switch.

This module was copied with some slight modifications from the example from:
'https://stackoverflow.com/questions/14780517/toggle-switch-in-qt' for the toggle switch.
Some additional integration methods for the custom widget plugin was adapter from the 
example code found from: 'https://www.riverbankcomputing.com/software/pyqt/download5'
in the folder: \examples\designer\plugins

"""

from PyQt5.QtCore import (QPropertyAnimation, QRectF, QSize, Qt, pyqtProperty,
                          pyqtSlot)
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import (QAbstractButton, QApplication, QHBoxLayout,
                             QSizePolicy, QWidget)


class SwitchButton(QAbstractButton):
    """Found from: https://stackoverflow.com/questions/14780517/toggle-switch-in-qt 
    """

    def __init__(self, parent=None, track_radius=15, thumb_radius=20):
        super().__init__(parent=parent)
        self.setCheckable(True)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self._track_radius = track_radius
        self._thumb_radius = thumb_radius

        self._margin = max(0, self._thumb_radius - self._track_radius)
        self._base_offset = max(self._thumb_radius, self._track_radius)
        self._end_offset = {
            True: lambda: self.width() - self._base_offset,
            False: lambda: self._base_offset,
        }
        self._offset = self._base_offset

        palette = self.palette()
        if self._thumb_radius > self._track_radius:
            self._track_color = {
                True: palette.highlight(),
                False: palette.dark(),
            }
            self._thumb_color = {
                True: palette.highlight(),
                False: palette.light(),
            }
            self._text_color = {
                True: palette.highlightedText().color(),
                False: palette.dark().color(),
            }
            self._thumb_text = {
                True: '',
                False: '',
            }
            self._track_opacity = 0.5
        else:
            self._thumb_color = {
                True: palette.highlightedText(),
                False: palette.light(),
            }
            self._track_color = {
                True: palette.highlight(),
                False: palette.dark(),
            }
            self._text_color = {
                True: palette.highlight().color(),
                False: palette.dark().color(),
            }
            self._thumb_text = {
                True: '✔',
                False: '✕',
            }
            self._track_opacity = 1

    @pyqtProperty(int)
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = value
        self.update()

    def sizeHint(self):  # pylint: disable=invalid-name
        return QSize(
            4 * self._track_radius + 2 * self._margin,
            2 * self._track_radius + 2 * self._margin,
        )

    def setChecked(self, checked):
        super().setChecked(checked)
        self.offset = self._end_offset[checked]()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.offset = self._end_offset[self.isChecked()]()

    def paintEvent(self, event):  # pylint: disable=invalid-name, unused-argument
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setPen(Qt.NoPen)
        track_opacity = self._track_opacity
        thumb_opacity = 1.0
        text_opacity = 1.0

        if self._thumb_radius > self._track_radius:
            self._thumb_text = {
                True: '',
                False: '',
            }
        else:
            self._thumb_text = {
                True: '✔',
                False: '✕',
            }

        if self.isEnabled():
            track_brush = self._track_color[self.isChecked()]
            thumb_brush = self._thumb_color[self.isChecked()]
            text_color = self._text_color[self.isChecked()]
        else:
            track_opacity *= 0.8
            track_brush = self.palette().shadow()
            thumb_brush = self.palette().mid()
            text_color = self.palette().shadow().color()

        p.setBrush(track_brush)
        p.setOpacity(track_opacity)
        p.drawRoundedRect(
            self._margin,
            self._margin,
            self.width() - 2 * self._margin,
            self.height() - 2 * self._margin,
            self._track_radius,
            self._track_radius,
        )
        p.setBrush(thumb_brush)
        p.setOpacity(thumb_opacity)
        p.drawEllipse(
            self.offset - self._thumb_radius,
            self._base_offset - self._thumb_radius,
            2 * self._thumb_radius,
            2 * self._thumb_radius,
        )
        p.setPen(text_color)
        p.setOpacity(text_opacity)
        font = p.font()
        font.setPixelSize(1.5 * self._thumb_radius)
        p.setFont(font)
        p.drawText(
            QRectF(
                self.offset - self._thumb_radius,
                self._base_offset - self._thumb_radius,
                2 * self._thumb_radius,
                2 * self._thumb_radius,
            ),
            Qt.AlignCenter,
            self._thumb_text[self.isChecked()],
        )

    def mouseReleaseEvent(self, event):  # pylint: disable=invalid-name
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            anim = QPropertyAnimation(self, b'offset', self)
            anim.setDuration(120)
            anim.setStartValue(self.offset)
            anim.setEndValue(self._end_offset[self.isChecked()]())
            anim.start()

    def set_switch_off(self):
        anim = QPropertyAnimation(self, b'offset', self)
        anim.setDuration(120)
        anim.setStartValue(self.offset)
        anim.setEndValue(self._end_offset[self.isChecked()]())
        anim.start()

    def enterEvent(self, event):  # pylint: disable=invalid-name
        self.setCursor(Qt.PointingHandCursor)
        super().enterEvent(event)

    # The thumb_radius property is implemented using the get_thumb_radius() getter
    # method, the set_thumb_radius() setter method, and the reset_thumb_radius() method.

    # The getter just returns the internal thumb_radius value.
    def get_thumb_radius(self):
        return self._thumb_radius

    # The set_thumb_radius() method is also defined to be a slot. The @pyqtSlot
    # decorator is used to tell PyQt which argument type the method expects,
    # and is especially useful when you want to define slots with the same
    # name that accept different argument types.

    @pyqtSlot(int)
    def set_thumb_radius(self, value):

        self._thumb_radius = value

        self._margin = max(0, self._thumb_radius - self._track_radius)
        self._base_offset = max(self._thumb_radius, self._track_radius)
        self._end_offset = {
            True: lambda: self.width() - self._base_offset,
            False: lambda: self._base_offset,
        }
        self._offset = self._base_offset

        self.update()

    # Qt's property system supports properties that can be reset to their
    # original values. This method enables the track_radius property to be reset.
    def reset_thumb_radius(self):

        self._thumb_radius = 0
        self.update()

    # The track_radius property is implemented using the get_track_radius() getter
    # method, the set_track_radius() setter method, and the reset_track_radius() method.

    # The getter just returns the internal thumb_radius value.
    def get_track_radius(self):
        return self._track_radius

    # The set_track_radius() method is also defined to be a slot. The @pyqtSlot
    # decorator is used to tell PyQt which argument type the method expects,
    # and is especially useful when you want to define slots with the same
    # name that accept different argument types.

    @pyqtSlot(int)
    def set_track_radius(self, value):

        self._track_radius = value

        self._margin = max(0, self._thumb_radius - self._track_radius)
        self._base_offset = max(self._thumb_radius, self._track_radius)
        self._end_offset = {
            True: lambda: self.width() - self._base_offset,
            False: lambda: self._base_offset,
        }
        self._offset = self._base_offset

        self.update()

    # Qt's property system supports properties that can be reset to their
    # original values. This method enables the track_radius property to be reset.
    def reset_track_radius(self):

        self._track_radius = 0
        self.update()

    thumb_radius = pyqtProperty(
        int, get_thumb_radius, set_thumb_radius, reset_thumb_radius)
    track_radius = pyqtProperty(
        int, get_track_radius, set_track_radius, reset_track_radius)
