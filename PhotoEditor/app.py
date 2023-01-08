import sys
import PyQt5
import cv2.cv2
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QFileDialog, QLabel, QMainWindow
import source
import utils
from custom_label import CustomLabel
from utils import *

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


# function to create different fonts
def create_font(size=12):
    font = QtGui.QFont()
    font.setFamily("MS Reference Sans Serif")
    font.setPointSize(size)
    font.setWeight(50)
    return font


class MainApp(QMainWindow):
    filename = None
    tmp_image = None
    image = None
    brightness_value_now = 0
    contrast_value_now = 0
    saturation_value_now = 0
    sigma_s_value_now = 0
    sigma_r_value_now = 0
    special_filter_flag = 0  # 1-HDR, 2-cartoon, 3-pencil sketch grey, 4-pencil sketch color
    change_tab_flag = 0  # only when it is set to 1 we can navigate through tabs

    def __init__(self):
        super().__init__()
        self.setupUi()
        self.handle_tabs()
        self.handle_exit()
        self.handle_buttons()
        self.handle_sliders()
        self.handle_combo_boxes()
        # enable is set to false
        self.edit_stacked_widget.setEnabled(False)
        self.layout_widget2.setEnabled(False)

    def setupUi(self):
        self.setObjectName("main-form")
        self.resize(780, 390)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setStyleSheet("QPushButton {\n"
                           "    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(128, 64, 0, 255), stop:1 rgba(255, 255, 255, 255));\n"
                           "    border-radius:5px;\n"
                           "    border:1 px solid orange;\n"
                           "    color:rgb(78, 0, 0);\n"
                           "}\n"
                           "\n"
                           "QLabel[objectName^=\"main_label\"] {\n"
                           "    background-image: url(:/resources/background.jpg);\n"
                           "    border-radius:15px;\n"
                           "}\n"
                           "\n"
                           "QPushButton::pressed{\n"
                           "    padding-left:3 px;\n"
                           "    padding-top:3 px;\n"
                           "}\n"
                           "\n"
                           "QStackedWidget {\n"
                           "    background:rgba(130, 65, 0,0.4);\n"
                           "    border: 3px groove rgb(188, 94, 0);\n"
                           "}\n"
                           "\n"
                           "QLabel {\n"
                           "    color:rgb(255, 235, 225);\n"
                           "}\n"
                           "\n"
                           "QComboBox {\n"
                           "    border: 1px solid orange;\n"
                           "    border-radius: 5px;\n"
                           "    color:rgb(255, 235, 225);\n"
                           "    background-color:rgba(160, 43, 5,0.6);\n"
                           "}\n"
                           "\n"
                           "QComboBox QAbstractItemView {\n"
                           "    border: 2px solid rgb(204, 105, 72);\n"
                           "    background-color:rgba(160, 43, 5,0.3);\n"
                           "    selection-background-color: rgb(255, 195, 151);\n"
                           "    color:rgb(240, 160, 95);\n"
                           "}\n"
                           "\n"
                           "QSlider::groove:horizontal {\n"
                           "    border: 1px solid #999999;\n"
                           "    height: 10px;\n"
                           "    background: qconicalgradient(cx:0.5, cy:0.5, angle:0, stop:0 rgba(35, 40, 3, 255), stop:0.16 rgba(136, 106, 22, 255), stop:0.225 rgba(166, 140, 41, 255), stop:0.285 rgba(204, 181, 74, 255), stop:0.345 rgba(235, 219, 102, 255), stop:0.415 rgba(245, 236, 112, 255), stop:0.52 rgba(209, 190, 76, 255), stop:0.57 rgba(187, 156, 51, 255), stop:0.635 rgba(168, 142, 42, 255), stop:0.695 rgba(202, 174, 68, 255), stop:0.75 rgba(218, 202, 86, 255),   stop:0.815 rgba(208, 187, 73, 255), stop:0.88 rgba(187, 156, 51, 255), stop:0.935 rgba(137, 108, 26, 255), stop:1 rgba(35, 40, 3, 255));\n"
                           "    margin: 2px 0;\n"
                           "    border-radius:3px;\n"
                           "}\n"
                           "\n"
                           "QSlider::handle:horizontal {\n"
                           "    background: qconicalgradient(cx:0.5, cy:0.5, angle:0, stop:0 rgba(35, 40, 3, 255), stop:0.16 rgba(136, 106, 22, 255), stop:0.225 rgba(166, 140, 41, 255), stop:0.285 rgba(204, 181, 74, 255), stop:0.345 rgba(235, 219, 102, 255), stop:0.415 rgba(245, 236, 112, 255), stop:0.52 rgba(209, 190, 76, 255), stop:0.57 rgba(187, 156, 51, 255), stop:0.635 rgba(168, 142, 42, 255), stop:0.695 rgba(202, 174, 68, 255), stop:0.75 rgba(218, 202, 86, 255), stop:0.815 rgba(208, 187, 73, 255), stop:0.88 rgba(187, 156, 51, 255), stop:0.935 rgba(137, 108, 26, 255), stop:1 rgba(35, 40, 3, 255));\n"
                           "    border: 1px solid #5c5c5c;\n"
                           "    width: 10px;\n"
                           "    margin:-6px 0;\n"
                           "}\n"
                           "\n"
                           "QPushButton[objectName^=\"go_btn\"]{\n"
                           "background-color:transparent;\n"
                           "}")

        # main_label - container of all
        self.main_label = QLabel(self)
        self.main_label.setGeometry(QtCore.QRect(10, 10, 760, 360))
        self.main_label.setObjectName("main_label")

        # image_label - container of image
        self.image_label = CustomLabel(self)
        self.image_label.setGeometry(QtCore.QRect(55, 30, 270, 270))
        self.image_label.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.image_label.setScaledContents(False)
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.image_label.setObjectName("image_label")

        # font object
        normal_font = create_font()
        big_font = create_font(15)
        small_font = create_font(8)
        very_small_font = create_font(6)
        paint_page_font = create_font(10)

        # icons
        right_arrow_icon = QtGui.QIcon()
        right_arrow_icon.addPixmap(QtGui.QPixmap(":/resources/right-arrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        left_arrow_icon = QtGui.QIcon()
        left_arrow_icon.addPixmap(QtGui.QPixmap(":/resources/left-arrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        cross_icon = QtGui.QIcon()
        cross_icon.addPixmap(QtGui.QPixmap(":/resources/cross-mark.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        check_icon = QtGui.QIcon()
        check_icon.addPixmap(QtGui.QPixmap(":/resources/check-mark.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        # buttons
        self.browse_btn = QtWidgets.QPushButton(self)
        self.browse_btn.setGeometry(QtCore.QRect(40, 320, 60, 30))
        self.browse_btn.setFont(normal_font)
        self.browse_btn.setObjectName("browse_btn")

        self.exit_btn = QtWidgets.QPushButton(self)
        self.exit_btn.setGeometry(QtCore.QRect(700, 330, 60, 30))
        self.exit_btn.setFont(normal_font)
        self.exit_btn.setObjectName("exit_btn")

        self.save_btn = QtWidgets.QPushButton(self)
        self.save_btn.setGeometry(QtCore.QRect(120, 320, 60, 30))
        self.save_btn.setFont(normal_font)
        self.save_btn.setObjectName("save_btn")

        self.crop_btn = QtWidgets.QPushButton(self)
        self.crop_btn.setGeometry(QtCore.QRect(280, 320, 60, 30))
        self.crop_btn.setFont(normal_font)
        self.crop_btn.setObjectName("crop_btn")

        self.rotate_btn = QtWidgets.QPushButton(self)
        self.rotate_btn.setGeometry(QtCore.QRect(200, 320, 60, 30))
        self.rotate_btn.setFont(normal_font)
        self.rotate_btn.setObjectName("rotate_btn")

        # the editor
        self.edit_stacked_widget = QtWidgets.QStackedWidget(self)
        self.edit_stacked_widget.setGeometry(QtCore.QRect(390, 35, 360, 260))
        self.edit_stacked_widget.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.edit_stacked_widget.setObjectName("edit_stacked_widget")

        # adjust tab
        self.adjust_page = QtWidgets.QWidget()
        self.adjust_page.setObjectName("adjust_page")

        self.saturation_label = QtWidgets.QLabel(self.adjust_page)
        self.saturation_label.setGeometry(QtCore.QRect(20, 160, 91, 31))
        self.saturation_label.setFont(normal_font)

        self.brightness_label = QtWidgets.QLabel(self.adjust_page)
        self.brightness_label.setGeometry(QtCore.QRect(20, 90, 101, 20))
        self.brightness_label.setFont(normal_font)

        self.contrast_label = QtWidgets.QLabel(self.adjust_page)
        self.contrast_label.setGeometry(QtCore.QRect(20, 130, 91, 16))
        self.contrast_label.setFont(normal_font)

        self.layout_widget = QtWidgets.QWidget(self.adjust_page)
        self.layout_widget.setGeometry(QtCore.QRect(130, 70, 201, 141))

        self.vertical_layout = QtWidgets.QVBoxLayout(self.layout_widget)
        self.vertical_layout.setContentsMargins(0, 0, 0, 0)

        self.brightness_slider = QtWidgets.QSlider(self.layout_widget)
        self.brightness_slider.setMinimum(-100)
        self.brightness_slider.setMaximum(100)
        self.brightness_slider.setOrientation(QtCore.Qt.Horizontal)
        self.brightness_slider.setObjectName("brightness_slider")

        self.vertical_layout.addWidget(self.brightness_slider)
        self.contrast_slider = QtWidgets.QSlider(self.layout_widget)
        self.contrast_slider.setMinimum(-15)
        self.contrast_slider.setMaximum(15)
        self.contrast_slider.setOrientation(QtCore.Qt.Horizontal)
        self.contrast_slider.setObjectName("contrast_slider")
        self.vertical_layout.addWidget(self.contrast_slider)

        self.saturation_slider = QtWidgets.QSlider(self.layout_widget)
        self.saturation_slider.setMinimum(-300)
        self.saturation_slider.setMaximum(300)
        self.saturation_slider.setOrientation(QtCore.Qt.Horizontal)
        self.saturation_slider.setObjectName("saturation_slider")
        self.vertical_layout.addWidget(self.saturation_slider)

        self.adjust_label = QtWidgets.QLabel(self.adjust_page)
        self.adjust_label.setGeometry(QtCore.QRect(150, 20, 101, 25))
        self.adjust_label.setFont(big_font)
        self.adjust_label.setObjectName("adjust_lable")

        self.go_btn_0 = QtWidgets.QPushButton(self.adjust_page)
        self.go_btn_0.setGeometry(QtCore.QRect(315, 0, 40, 40))
        self.go_btn_0.setFont(normal_font)
        self.go_btn_0.setIcon(right_arrow_icon)
        self.go_btn_0.setIconSize(QtCore.QSize(40, 40))
        self.go_btn_0.setObjectName("go_btn_0")

        self.edit_stacked_widget.addWidget(self.adjust_page)

        # filters tab

        self.filters_page = QtWidgets.QWidget()
        self.filters_page.setObjectName("filters_page")

        self.sepia_btn = QtWidgets.QPushButton(self.filters_page)
        self.sepia_btn.setGeometry(QtCore.QRect(15, 60, 90, 25))
        self.sepia_btn.setFont(small_font)
        self.sepia_btn.setObjectName("sepia_btn")

        self.greyscale_btn = QtWidgets.QPushButton(self.filters_page)
        self.greyscale_btn.setGeometry(QtCore.QRect(15, 95, 90, 25))
        self.greyscale_btn.setFont(small_font)
        self.greyscale_btn.setObjectName("greyscale_btn")

        self.gaussian_blur_btn = QtWidgets.QPushButton(self.filters_page)
        self.gaussian_blur_btn.setGeometry(QtCore.QRect(15, 130, 90, 25))
        self.gaussian_blur_btn.setFont(small_font)
        self.gaussian_blur_btn.setObjectName("gaussian_blur_btn")

        self.median_blur_btn = QtWidgets.QPushButton(self.filters_page)
        self.median_blur_btn.setGeometry(QtCore.QRect(15, 165, 90, 25))
        self.median_blur_btn.setFont(small_font)
        self.median_blur_btn.setObjectName("median_blur_btn")

        self.summer_effect_btn = QtWidgets.QPushButton(self.filters_page)
        self.summer_effect_btn.setGeometry(QtCore.QRect(135, 60, 90, 25))
        self.summer_effect_btn.setFont(small_font)
        self.summer_effect_btn.setObjectName("summer_effect_btn")

        self.winter_effect_btn = QtWidgets.QPushButton(self.filters_page)
        self.winter_effect_btn.setGeometry(QtCore.QRect(135, 95, 90, 25))
        self.winter_effect_btn.setFont(small_font)
        self.winter_effect_btn.setObjectName("winter_effect_btn")

        self.hdr_btn = QtWidgets.QPushButton(self.filters_page)
        self.hdr_btn.setGeometry(QtCore.QRect(135, 130, 90, 25))
        self.hdr_btn.setFont(small_font)
        self.hdr_btn.setObjectName("hdr_btn")

        self.sharpen_btn = QtWidgets.QPushButton(self.filters_page)
        self.sharpen_btn.setGeometry(QtCore.QRect(135, 165, 90, 25))
        self.sharpen_btn.setFont(small_font)
        self.sharpen_btn.setObjectName("sharpen_btn")

        self.pencil_sketch_grey_btn = QtWidgets.QPushButton(self.filters_page)
        self.pencil_sketch_grey_btn.setGeometry(QtCore.QRect(250, 60, 90, 25))
        self.pencil_sketch_grey_btn.setFont(small_font)
        self.pencil_sketch_grey_btn.setObjectName("pencil_sketch_grey_btn")

        self.pencil_sketch_color_btn = QtWidgets.QPushButton(self.filters_page)
        self.pencil_sketch_color_btn.setGeometry(QtCore.QRect(250, 95, 90, 25))
        self.pencil_sketch_color_btn.setFont(small_font)
        self.pencil_sketch_color_btn.setObjectName("pencil_sketch_color_btn")

        self.cartoon_btn = QtWidgets.QPushButton(self.filters_page)
        self.cartoon_btn.setGeometry(QtCore.QRect(250, 130, 90, 25))
        self.cartoon_btn.setFont(small_font)
        self.cartoon_btn.setObjectName("cartoon_btn")

        self.invert_btn = QtWidgets.QPushButton(self.filters_page)
        self.invert_btn.setGeometry(QtCore.QRect(250, 165, 90, 25))
        self.invert_btn.setFont(small_font)
        self.invert_btn.setObjectName("invert_btn")

        self.filters_label = QtWidgets.QLabel(self.filters_page)
        self.filters_label.setGeometry(QtCore.QRect(150, 20, 80, 20))
        self.filters_label.setFont(big_font)
        self.filters_label.setObjectName("filters_label")

        self.go_btn_1 = QtWidgets.QPushButton(self.filters_page)
        self.go_btn_1.setGeometry(QtCore.QRect(315, 0, 40, 40))
        self.go_btn_1.setFont(normal_font)
        self.go_btn_1.setIcon(right_arrow_icon)
        self.go_btn_1.setIconSize(QtCore.QSize(40, 40))
        self.go_btn_1.setObjectName("go_btn_1")

        self.go_btn_2 = QtWidgets.QPushButton(self.filters_page)
        self.go_btn_2.setGeometry(QtCore.QRect(0, 0, 40, 40))
        self.go_btn_2.setFont(normal_font)
        self.go_btn_2.setIcon(left_arrow_icon)
        self.go_btn_2.setIconSize(QtCore.QSize(40, 40))
        self.go_btn_2.setObjectName("go_btn_2")

        self.observation_label = QtWidgets.QLabel(self.filters_page)
        self.observation_label.setGeometry(QtCore.QRect(15, 200, 270, 20))
        self.observation_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.observation_label.setFont(very_small_font)
        self.observation_label.setObjectName("observation_label")

        self.layout_widget2 = QtWidgets.QWidget(self.filters_page)
        self.layout_widget2.setGeometry(QtCore.QRect(15, 215, 320, 40))

        self.horizontal_layout = QtWidgets.QHBoxLayout(self.layout_widget2)
        self.horizontal_layout.setContentsMargins(5, 0, 0, 0)

        self.sigma_s_label = QtWidgets.QLabel(self.layout_widget2)
        self.sigma_s_label.setFont(small_font)
        self.horizontal_layout.addWidget(self.sigma_s_label)

        self.sigma_s_slider = QtWidgets.QSlider(self.layout_widget2)
        self.sigma_s_slider.setMinimum(-99)
        self.sigma_s_slider.setMaximum(99)
        self.sigma_s_slider.setOrientation(QtCore.Qt.Horizontal)
        self.sigma_s_slider.setObjectName("sigma_s_slider")
        self.horizontal_layout.addWidget(self.sigma_s_slider)

        self.sigma_r_label = QtWidgets.QLabel(self.layout_widget2)
        self.sigma_r_label.setFont(small_font)
        self.horizontal_layout.addWidget(self.sigma_r_label)

        self.sigma_r_slider = QtWidgets.QSlider(self.layout_widget2)
        self.sigma_r_slider.setMinimum(-49)
        self.sigma_r_slider.setMaximum(49)
        self.sigma_r_slider.setOrientation(QtCore.Qt.Horizontal)
        self.sigma_r_slider.setObjectName("sigma_r_slider")
        self.horizontal_layout.addWidget(self.sigma_r_slider)

        self.edit_stacked_widget.addWidget(self.filters_page)

        # paint page

        self.paint_page = QtWidgets.QWidget()
        self.paint_page.setObjectName("paint_page")

        self.figure_combo_box = QtWidgets.QComboBox(self.paint_page)
        self.figure_combo_box.setGeometry(QtCore.QRect(190, 155, 110, 22))
        self.figure_combo_box.setFont(paint_page_font)
        self.figure_combo_box.setObjectName("figure_combo_box")
        self.figure_combo_box.addItem("")
        self.figure_combo_box.addItem("")
        self.figure_combo_box.addItem("")

        self.pen_color_combo_box = QtWidgets.QComboBox(self.paint_page)
        self.pen_color_combo_box.setGeometry(QtCore.QRect(190, 115, 110, 22))
        self.pen_color_combo_box.setFont(paint_page_font)
        self.pen_color_combo_box.setObjectName("pen_color_combo_box")
        self.pen_color_combo_box.addItem("")
        self.pen_color_combo_box.addItem("")
        self.pen_color_combo_box.addItem("")
        self.pen_color_combo_box.addItem("")
        self.pen_color_combo_box.addItem("")

        self.pen_size_combo_box = QtWidgets.QComboBox(self.paint_page)
        self.pen_size_combo_box.setGeometry(QtCore.QRect(190, 75, 110, 22))
        self.pen_size_combo_box.setFont(paint_page_font)
        self.pen_size_combo_box.setObjectName("pen_size_combo_box")
        self.pen_size_combo_box.addItem("")
        self.pen_size_combo_box.addItem("")
        self.pen_size_combo_box.addItem("")
        self.pen_size_combo_box.addItem("")

        self.size_label = QtWidgets.QLabel(self.paint_page)
        self.size_label.setGeometry(QtCore.QRect(50, 75, 150, 20))
        self.size_label.setFont(paint_page_font)
        self.size_label.setObjectName("size_lable")

        self.color_label = QtWidgets.QLabel(self.paint_page)
        self.color_label.setGeometry(QtCore.QRect(50, 115, 150, 20))
        self.color_label.setFont(paint_page_font)
        self.color_label.setObjectName("color_lable")

        self.figure_label = QtWidgets.QLabel(self.paint_page)
        self.figure_label.setGeometry(QtCore.QRect(50, 155, 150, 20))
        self.figure_label.setFont(paint_page_font)
        self.figure_label.setObjectName("figure-label")

        self.paint_btn = QtWidgets.QPushButton(self.paint_page)
        self.paint_btn.setGeometry(QtCore.QRect(150, 210, 60, 30))
        self.paint_btn.setFont(normal_font)
        self.paint_btn.setObjectName("paint_btn")

        self.paint_label = QtWidgets.QLabel(self.paint_page)
        self.paint_label.setGeometry(QtCore.QRect(150, 20, 61, 20))
        self.paint_label.setFont(big_font)
        self.paint_label.setObjectName("paint_label")

        self.go_btn_3 = QtWidgets.QPushButton(self.paint_page)
        self.go_btn_3.setGeometry(QtCore.QRect(0, 0, 40, 40))
        self.go_btn_3.setFont(normal_font)
        self.go_btn_3.setIcon(left_arrow_icon)
        self.go_btn_3.setIconSize(QtCore.QSize(40, 40))
        self.go_btn_3.setObjectName("go_btn_2")

        self.edit_stacked_widget.addWidget(self.paint_page)

        # apply and cancel buttons
        self.cancel_btn = QtWidgets.QPushButton(self)
        self.cancel_btn.setGeometry(QtCore.QRect(585, 310, 30, 30))
        self.cancel_btn.setFont(small_font)
        self.cancel_btn.setIcon(cross_icon)
        self.cancel_btn.setIconSize(QtCore.QSize(25, 25))
        self.cancel_btn.setObjectName("cancel_btn")

        self.apply_btn = QtWidgets.QPushButton(self)
        self.apply_btn.setGeometry(QtCore.QRect(530, 310, 30, 30))
        self.apply_btn.setFont(small_font)
        self.apply_btn.setIcon(check_icon)
        self.apply_btn.setIconSize(QtCore.QSize(25, 25))
        self.apply_btn.setObjectName("apply_btn")

        self.retranslateUi()
        self.edit_stacked_widget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("main_form", "Form"))
        self.browse_btn.setText(_translate("main_form", "Browse"))
        self.exit_btn.setText(_translate("main_form", "Exit"))
        self.save_btn.setText(_translate("main_form", "Save"))
        self.crop_btn.setText(_translate("main_form", "Crop"))
        self.rotate_btn.setText(_translate("main_form", "Rotate"))
        self.saturation_label.setText(_translate("main_form", "Saturation"))
        self.brightness_label.setText(_translate("main_form", "Brightness"))
        self.observation_label.setText(
            (_translate("main__form", "Available for cartoon,HDR and pencil sketch filters!")))
        self.contrast_label.setText(_translate("main_form", "Contrast"))
        self.sigma_s_label.setText(_translate("main_form", "sigma_s"))
        self.sigma_r_label.setText(_translate("main_form", "sigma_r"))
        self.adjust_label.setText(_translate("main_form", "Adjust"))
        self.pencil_sketch_color_btn.setText(_translate("main_form", "Pencil Sketch 2"))
        self.greyscale_btn.setText(_translate("main_form", "Greyscale"))
        self.gaussian_blur_btn.setText(_translate("main_form", "Gaussian Blur"))
        self.sharpen_btn.setText(_translate("main_form", "Sharpen"))
        self.summer_effect_btn.setText(_translate("main_form", "Summer Effect"))
        self.hdr_btn.setText(_translate("main_form", "HDR"))
        self.pencil_sketch_grey_btn.setText(_translate("main_form", "Pencil Sketch 1"))
        self.winter_effect_btn.setText(_translate("main_form", "Winter Effect"))
        self.sepia_btn.setText(_translate("main_form", "Sepia"))
        self.median_blur_btn.setText(_translate("main_form", "Median Blur"))
        self.cartoon_btn.setText(_translate("main_form", "Cartoon"))
        self.filters_label.setText(_translate("main_form", "Filters"))
        self.invert_btn.setText(_translate("main_form", "Invert"))
        self.figure_combo_box.setItemText(0, _translate("main_form", "Line"))
        self.figure_combo_box.setItemText(1, _translate("main_form", "Rectangle"))
        self.figure_combo_box.setItemText(2, _translate("main_form", "Circle"))
        self.pen_color_combo_box.setItemText(0, _translate("main_form", "Red"))
        self.pen_color_combo_box.setItemText(1, _translate("main_form", "Green"))
        self.pen_color_combo_box.setItemText(2, _translate("main_form", "Black"))
        self.pen_color_combo_box.setItemText(3, _translate("main_form", "White"))
        self.pen_color_combo_box.setItemText(4, _translate("main_form", "Blue"))
        self.pen_size_combo_box.setItemText(0, _translate("main_form", "Thin"))
        self.pen_size_combo_box.setItemText(1, _translate("main_form", "Medium"))
        self.pen_size_combo_box.setItemText(2, _translate("main_form", "Thick"))
        self.pen_size_combo_box.setItemText(3, _translate("main_form", "Fill"))
        self.size_label.setText(_translate("main_form", "Select pen size:"))
        self.color_label.setText(_translate("main_form", "Select pen color:"))
        self.figure_label.setText(_translate("main_form", "Select figure:"))
        self.paint_btn.setText(_translate("main_form", "Paint"))
        self.paint_label.setText(_translate("main_form", "Paint"))

    ####################### Connect widgets to functions ######################

    def handle_tabs(self):
        self.go_btn_0.clicked.connect(lambda: self.edit_stacked_widget.setCurrentIndex(1))
        self.go_btn_1.clicked.connect(lambda: self.edit_stacked_widget.setCurrentIndex(2))
        self.go_btn_2.clicked.connect(lambda: self.edit_stacked_widget.setCurrentIndex(0))
        self.go_btn_3.clicked.connect(lambda: self.edit_stacked_widget.setCurrentIndex(1))

    def go_buttons_change(self):
        if self.change_tab_flag == 0:
            self.go_btn_0.setEnabled(False)
            self.go_btn_1.setEnabled(False)
            self.go_btn_2.setEnabled(False)
            self.go_btn_3.setEnabled(False)
        else:
            self.go_btn_0.setEnabled(True)
            self.go_btn_1.setEnabled(True)
            self.go_btn_2.setEnabled(True)
            self.go_btn_3.setEnabled(True)

    def handle_exit(self):
        self.exit_btn.clicked.connect(lambda: sys.exit())

    def handle_buttons(self):
        self.browse_btn.clicked.connect(self.load_image)
        self.save_btn.clicked.connect(self.save_image)
        self.rotate_btn.clicked.connect(self.rotate_image)
        self.crop_btn.clicked.connect(self.crop_image)
        self.sepia_btn.clicked.connect(self.sepia_effect)
        self.greyscale_btn.clicked.connect(self.greyscale_effect)
        self.gaussian_blur_btn.clicked.connect(self.gaussian_blur_effect)
        self.median_blur_btn.clicked.connect(self.median_blur_effect)
        self.sharpen_btn.clicked.connect(self.sharpen_effect)
        self.invert_btn.clicked.connect(self.invert_effect)
        self.summer_effect_btn.clicked.connect(self.summer_effect)
        self.winter_effect_btn.clicked.connect(self.winter_effect)
        self.pencil_sketch_color_btn.clicked.connect(self.pencil_sketch_color_effect)
        self.pencil_sketch_grey_btn.clicked.connect(self.pencil_sketch_grey_effect)
        self.cartoon_btn.clicked.connect(self.cartoon_effect)
        self.hdr_btn.clicked.connect(self.hdr_effect)
        self.paint_btn.clicked.connect(self.paint)
        self.apply_btn.clicked.connect(self.apply_changes)
        self.cancel_btn.clicked.connect(self.delete_changes)

    def handle_combo_boxes(self):
        self.figure_combo_box.activated.connect(self.get_figure)
        self.pen_size_combo_box.activated.connect(self.get_pen_size)
        self.pen_color_combo_box.activated.connect(self.get_pen_color)

    def handle_sliders(self):
        self.brightness_slider.valueChanged['int'].connect(self.brightness_value)
        self.saturation_slider.valueChanged['int'].connect(self.saturation_value)
        self.contrast_slider.valueChanged['int'].connect(self.contrast_value)
        self.sigma_s_slider.valueChanged['int'].connect(self.sigma_s_value)
        self.sigma_r_slider.valueChanged['int'].connect(self.sigma_r_value)

    #####################  Save,Rotate,Crop,Load Events ####################

    def load_image(self):
        self.filename = QFileDialog.getOpenFileName(filter="Image (*.*)")[0]
        if self.filename:
            self.image = cv2.imread(self.filename)
            self.set_photo(self.image)
        self.edit_stacked_widget.setEnabled(True)

    def set_photo(self, image):
        image = utils.resize_image(image)
        self.tmp_image = image
        self.image_label.set_image(self.tmp_image)
        frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(image)
        self.image_label.setPixmap(pixmap)
        self.go_buttons_change()

    def save_image(self):
        filename = QFileDialog.getSaveFileName(filter="JPG(*.jpg);;PNG(*.png);;TIFF(*.tiff);;BMP(*.bmp)")[0]
        if filename:
            self.image_label.pixmap().save(filename)

    def rotate_image(self):
        self.change_tab_flag = 0
        image = rotate(self.tmp_image)
        self.set_photo(image)

    def crop_image(self):
        self.change_tab_flag = 0
        self.image_label.set_crop_flag()
        self.set_photo(self.image_label.get_image())


    ################################ Sliders - Adjust Tab and 2 sliders from Filters Tab ###############################

    def brightness_value(self, value):
        self.brightness_value_now = value
        self.update_sliders()

    def contrast_value(self, value):
        self.contrast_value_now = value
        self.update_sliders()

    def saturation_value(self, value):
        self.saturation_value_now = value
        self.update_sliders()

    def sigma_s_value(self, value):
        self.sigma_s_value_now = value
        self.update_sliders()

    def sigma_r_value(self, value):
        self.sigma_r_value_now = value
        self.update_sliders()

    def update_sliders(self):
        self.change_tab_flag = 0
        self.set_photo(self.image)
        image = adjust_brightness_contrast(self.image, self.contrast_value_now / 15 + 1.5,
                                           self.brightness_value_now)
        image = change_saturation(image, self.saturation_value_now)
        if self.special_filter_flag == 1:
            image = HDR(self.image, self.sigma_s_value_now + 100, (self.sigma_r_value_now + 50) / 100)
        elif self.special_filter_flag == 2:
            image = cartoon(self.image, self.sigma_s_value_now + 100, (self.sigma_r_value_now + 50) / 100)
        elif self.special_filter_flag == 3:
            image = pencil_sketch_grey(self.image, self.sigma_s_value_now + 100,
                                       (self.sigma_r_value_now + 50) / 100)
        elif self.special_filter_flag == 4:
            image = pencil_sketch_color(self.image, self.sigma_s_value_now + 100,
                                        (self.sigma_r_value_now + 50) / 100)
        self.set_photo(image)

    ###################### Filters Tab #######################

    def sepia_effect(self):
        self.change_tab_flag = 0
        self.set_photo(self.image)
        self.special_filter_flag = 0
        self.layout_widget2.setEnabled(False)
        image = sepia(self.tmp_image)
        self.set_photo(image)

    def greyscale_effect(self):
        self.change_tab_flag = 0
        self.set_photo(self.image)
        self.special_filter_flag = 0
        self.layout_widget2.setEnabled(False)
        image = greyscale(self.tmp_image)
        self.set_photo(image)

    def gaussian_blur_effect(self):
        self.change_tab_flag = 0
        self.set_photo(self.image)
        self.special_filter_flag = 0
        self.layout_widget2.setEnabled(False)
        image = gaussian_blur(self.tmp_image)
        self.set_photo(image)

    def median_blur_effect(self):
        self.change_tab_flag = 0
        self.set_photo(self.image)
        self.special_filter_flag = 0
        self.layout_widget2.setEnabled(False)
        image = median_blur(self.tmp_image)
        self.set_photo(image)

    def sharpen_effect(self):
        self.change_tab_flag = 0
        self.set_photo(self.image)
        self.special_filter_flag = 0
        self.layout_widget2.setEnabled(False)
        image = sharpen(self.tmp_image)
        self.set_photo(image)

    def invert_effect(self):
        self.change_tab_flag = 0
        self.set_photo(self.image)
        self.special_filter_flag = 0
        self.layout_widget2.setEnabled(False)
        image = invert(self.tmp_image)
        self.set_photo(image)

    def summer_effect(self):
        self.change_tab_flag = 0
        self.set_photo(self.image)
        self.special_filter_flag = 0
        self.layout_widget2.setEnabled(False)
        image = summer_effect(self.tmp_image)
        self.set_photo(image)

    def winter_effect(self):
        self.change_tab_flag = 0
        self.set_photo(self.image)
        self.special_filter_flag = 0
        self.layout_widget2.setEnabled(False)
        image = winter_effect(self.tmp_image)
        self.set_photo(image)

    def pencil_sketch_color_effect(self):
        self.change_tab_flag = 0
        self.set_photo(self.image)
        self.special_filter_flag = 4
        self.layout_widget2.setEnabled(True)
        image = pencil_sketch_color(self.tmp_image)
        self.set_photo(image)

    def pencil_sketch_grey_effect(self):
        self.change_tab_flag = 0
        self.set_photo(self.image)
        self.special_filter_flag = 3
        self.layout_widget2.setEnabled(True)
        image = pencil_sketch_grey(self.tmp_image)
        self.set_photo(image)

    def cartoon_effect(self):
        self.change_tab_flag = 0
        self.set_photo(self.image)
        self.special_filter_flag = 2
        self.layout_widget2.setEnabled(True)
        image = cartoon(self.tmp_image)
        self.set_photo(image)

    def hdr_effect(self):
        self.change_tab_flag = 0
        self.set_photo(self.image)
        self.special_filter_flag = 1
        self.layout_widget2.setEnabled(True)
        image = HDR(self.tmp_image)
        self.set_photo(image)

    ###################  Paint Tab  ###########################

    def paint(self):
        self.change_tab_flag = 0
        self.image_label.set_color(self.get_pen_color())
        self.image_label.set_pen_size(self.get_pen_size())
        self.image_label.set_figure(self.get_figure())
        self.image_label.set_paint_flag()
        self.set_photo(self.image_label.get_image())

    def get_pen_size(self):
        pen_size_dict = {"Thin": 1, "Medium": 2, "Thick": 3, "Fill": -1}
        return pen_size_dict[str(self.pen_size_combo_box.currentText())]

    def get_pen_color(self):
        color_dict = {"Red": (0, 0, 255), "Black": (0, 0, 0), "White": (255, 255, 255),
                      "Blue": (255, 0, 0), "Green": (0, 255, 0)}
        return color_dict[str(self.pen_color_combo_box.currentText())]

    def get_figure(self):
        return str(self.figure_combo_box.currentText())

    #################### Apply and Cancel buttons ############################

    def apply_changes(self):
        self.change_tab_flag = 1
        self.image = self.tmp_image
        self.set_photo(self.tmp_image)

    def delete_changes(self):
        self.change_tab_flag = 1
        self.tmp_image = self.image
        self.set_photo(self.tmp_image)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ui = MainApp()
    ui.show()
    sys.exit(app.exec_())
