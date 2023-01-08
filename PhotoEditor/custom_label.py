import PyQt5
import numpy as np
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QRect, QPoint, Qt
from PyQt5.QtGui import QImage, QPainter, QPen
from PyQt5.QtWidgets import QLabel, QRubberBand
from cv2 import cv2
import utils
from utils import crop_img


# overeating QLabel to implement painting and cropping
class CustomLabel(QLabel):
    # coordinates (x0,y0) and (x1,y1)
    x0 = 0
    y0 = 0
    x1 = 0
    y1 = 0
    paint_flag = False
    crop_flag = False
    # this image is always the temporary image from main class
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    # parameters for painting on image
    pen_size = 1
    color = (0, 0, 255)
    figure = "Line"

    def __init__(self, parentQWidget=None):
        super(CustomLabel, self).__init__(parentQWidget)

    def get_image(self):
        return self.image

    def set_image(self, image):
        self.image = image

    def set_crop_flag(self):
        self.crop_flag = True

    def set_paint_flag(self):
        self.paint_flag = True

    def set_pen_size(self, size):
        self.pen_size = size

    def set_color(self, color):
        self.color = color

    def set_figure(self, figure):
        self.figure = figure

    # function to translate the color from RGB format to Qt format using a dictionary
    def get_pen_color_qt(self):
        color_dict = {(0, 0, 255): Qt.red, (0, 0, 0): Qt.black, (255, 255, 255): Qt.white,
                      (255, 0, 0): Qt.blue, (0, 255, 0): Qt.green}
        return color_dict[self.color]

    def mousePressEvent(self, event):
        if self.crop_flag:
            self.originQPoint = event.pos()
            self.currentQRubberBand = QRubberBand(QRubberBand.Rectangle, self)
            self.currentQRubberBand.setGeometry(QRect(self.originQPoint, QtCore.QSize()))
            self.currentQRubberBand.show()
        if self.paint_flag:
            self.x0 = event.x()
            self.y0 = event.y()

    def mouseMoveEvent(self, event):
        if self.crop_flag:
            self.currentQRubberBand.setGeometry(QRect(self.originQPoint, event.pos()).normalized())
        if self.paint_flag:
            self.x1 = event.x()
            self.y1 = event.y()
            self.update()

    # paint event whenever paint_flag is set on True to paint dynamically
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(self.get_pen_color_qt()))
        frame = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        image = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(image)
        painter.drawPixmap(self.rect(),
                           pixmap)
        if self.paint_flag:
            if self.x0 and self.y0 and self.x1 and self.y1:
                if self.figure == "Line":
                    painter.drawLine(QPoint(self.x0, self.y0), QPoint(self.x1, self.y1))
                # in case of rectangle, we use 4 lines
                elif self.figure == "Rectangle":
                    painter.drawLine(QPoint(self.x0, self.y0), QPoint(self.x1, self.y0))
                    painter.drawLine(QPoint(self.x0, self.y0), QPoint(self.x0, self.y1))
                    painter.drawLine(QPoint(self.x1, self.y1), QPoint(self.x1, self.y0))
                    painter.drawLine(QPoint(self.x1, self.y1), QPoint(self.x0, self.y1))
                else:
                    radius = round(((self.x1 - self.x0) ** 2 + (self.y1 - self.y0) ** 2) ** 0.5)
                    painter.drawEllipse(QPoint((self.x0 + self.x1) // 2, (self.y0 + self.y1) // 2), radius // 2,
                                        radius // 2)

    def mouseReleaseEvent(self, event):
        if self.crop_flag:
            self.currentQRubberBand.hide()
            currentQRect = self.currentQRubberBand.geometry()
            coordinates = currentQRect.getRect()
            self.image = crop_img(self.image, coordinates[1], coordinates[3] + coordinates[1],
                                  coordinates[0], coordinates[2] + coordinates[0])
            self.image = utils.resize_image(self.image)
            self.currentQRubberBand.deleteLater()
            frame = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            image = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
            self.setPixmap(QtGui.QPixmap.fromImage(image))
            self.crop_flag = False
        if self.paint_flag:
            if self.figure == "Line":
                # if user select "Line" and pen size is "Fill"(-1) we set pen size to 1
                if self.pen_size == -1:
                    self.pen_size = 1
                self.image = cv2.line(self.image, (self.x0, self.y0), (self.x1, self.y1), self.color, self.pen_size)
            elif self.figure == "Rectangle":
                self.image = cv2.rectangle(self.image, (self.x0, self.y0), (self.x1, self.y1), self.color,
                                           self.pen_size)
            else:
                radius = round(((self.x1 - self.x0) ** 2 + (self.y1 - self.y0) ** 2) ** 0.5)
                self.image = cv2.circle(self.image, ((self.x0 + self.x1) // 2, (self.y0 + self.y1) // 2), radius // 2,
                                        self.color,
                                        self.pen_size)
            frame = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            image = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
            self.setPixmap(QtGui.QPixmap.fromImage(image))
            # setting the points to 0
            self.x0, self.y0, self.x1, self.y1 = 0, 0, 0, 0
            self.paint_flag = False
