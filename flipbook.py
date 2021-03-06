import sys
import os
import math
import resource
from PIL import Image, ImageDraw, ImageFont
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import *

from frame import Frames

if os.name == 'posix':
    from UI import flipbook_UI_IOS as UI
elif os.name == 'nt':
    from UI import flipbook_UI_WINDOWS as UI

class Flipbook(UI.Ui_MainWindow, QMainWindow):
    def __init__(self):
        super(Flipbook, self).__init__()
        self.setupUi(self)
        self.l_logo.setPixmap(QPixmap(":logo/logo2.png"))
        """-----------------For mac-------------------"""
        if os.name == 'posix':
            self.fld_image_path.setAttribute(Qt.WA_MacShowFocusRect, 0)
            self.fld_filename.setAttribute(Qt.WA_MacShowFocusRect, 0)
            self.fld_out_path.setAttribute(Qt.WA_MacShowFocusRect, 0)
            self.sb_images_per_line.setAttribute(Qt.WA_MacShowFocusRect, 0)
            self.sb_increment.setAttribute(Qt.WA_MacShowFocusRect, 0)
            self.sb_vertical_line.setAttribute(Qt.WA_MacShowFocusRect, 0)
            self.sb_horizontal_line.setAttribute(Qt.WA_MacShowFocusRect, 0)
            self.sb_background_color_a.setAttribute(Qt.WA_MacShowFocusRect, 0)
            self.sb_background_color_b.setAttribute(Qt.WA_MacShowFocusRect, 0)
            self.sb_background_color_g.setAttribute(Qt.WA_MacShowFocusRect, 0)
            self.sb_background_color_r.setAttribute(Qt.WA_MacShowFocusRect, 0)
            self.sb_end_value.setAttribute(Qt.WA_MacShowFocusRect, 0)
            self.sb_start_value.setAttribute(Qt.WA_MacShowFocusRect, 0)
            self.sb_inc_value.setAttribute(Qt.WA_MacShowFocusRect, 0)
            self.sb_max_images.setAttribute(Qt.WA_MacShowFocusRect, 0)
        """-------------------------------------------"""

        self.img = None
        self.backup_img = None
        self.frames = Frames()
        self.current_tab = None
        self.txt_pattern = "Total frames count: {0}\n" \
                           "Current frame ID: {1}\n" \
                           "Frame size(px): {2}\n" \
                           "Frame mode: {3}\n"

        self.tabWidget.setCurrentWidget(self.tab_frames)
        self.tabWidget.currentChanged.connect(lambda: self.tab_changed())

        self.btn_image_path.clicked.connect(lambda: self.click_btn_image_path())
        self.btn_frames_path.clicked.connect(lambda: self.click_btn_frames_path())
        self.btn_out_path.clicked.connect(lambda: self.click_btn_outpath())
        self.btn_save.clicked.connect(lambda: self.click_btn_render())

        self.sb_images_per_line.valueChanged.connect(lambda: self.generate_mosaic())
        self.sb_max_images.valueChanged.connect(lambda: self.generate_mosaic())
        self.sb_increment.valueChanged.connect(lambda: self.generate_mosaic())
        self.sb_background_color_r.valueChanged.connect(lambda: self.generate_mosaic())
        self.sb_background_color_g.valueChanged.connect(lambda: self.generate_mosaic())
        self.sb_background_color_b.valueChanged.connect(lambda: self.generate_mosaic())
        self.sb_background_color_a.valueChanged.connect(lambda: self.generate_mosaic())

        self.sb_vertical_line.valueChanged.connect(lambda: self.changed_sb_frames_count())
        self.sb_horizontal_line.valueChanged.connect(lambda: self.changed_sb_frames_count())
        self.sl_frame.valueChanged.connect(lambda: self.changed_sl_frame())
        self.cb_valid_frame_range.currentIndexChanged.connect(lambda: self.valid_frame_range_changed())

    def tab_changed(self):
        if self.tabWidget.currentIndex() == 1:
            self.generate_mosaic()
        else:
            if len(self.frames):
                self.l_preview_image.setPixmap(update_preview(self.frames[self.sl_frame.value()], self.label_info()))

    def generate_mosaic(self):
        if len(self.frames):
            prev_img = create_mosaic(
                            self.frames,
                            self.sb_images_per_line.value(),
                            self.sb_max_images.value(),
                            self.sb_increment.value(),
                            (
                                self.sb_background_color_r.value(),
                                self.sb_background_color_g.value(),
                                self.sb_background_color_b.value(),
                                self.sb_background_color_a.value()
                            )
                        )
            self.l_preview_image.setPixmap(update_preview(prev_img, self.label_info(self.frames.outMosaic)))

    def valid_frame_range_changed(self):
        bool_ = True if self.cb_valid_frame_range.currentIndex() == 1 else 0
        self.sb_start_value.setEnabled(bool_)
        self.sb_end_value.setEnabled(bool_)
        self.sb_inc_value.setEnabled(bool_)

    def click_btn_frames_path(self):
        files, ext = QFileDialog.getOpenFileNames(
            self, 'Open File', "", 'Images(*.png *.jpg *.jpeg *.tga *.psd)')
        if files:
            self.frames.__del__()
            for file in files:
                self.frames.framesList = Image.open(file)
            self.sb_max_images.setMaximum(len(self.frames))
            self.sb_images_per_line.setMaximum(len(self.frames))
            self.sl_frame.setMaximum(len(self.frames)-1)
            self.sb_start_value.setMaximum(len(self.frames))
            self.sb_end_value.setMaximum(len(self.frames))
            self.generate_mosaic()

    def click_btn_outpath(self):
        path = QFileDialog.getExistingDirectory(self, "Out Directory", "")
        if path:
            self.fld_out_path.setText(path)

    def click_btn_render(self):
        if self.fld_out_path.text():
            if len(self.frames):
                self.render()
            else:
                self.statusbar.showMessage("No Frames!", 3000)
        else:
            self.statusbar.showMessage("Please, select the output directory!", 3000)

    def click_btn_image_path(self):
        path, ext = QFileDialog.getOpenFileName(self, "Select Image", "", 'Images(*.png *.jpg *.jpeg *.tga *.psd)')
        if path:
            self.fld_image_path.setText(path)
            self.img = self.backup_img = Image.open(path)
            self.frames.__del__()
            self.sb_horizontal_line.setValue(1)
            self.sb_vertical_line.setValue(1)
            self.changed_sb_frames_count()

    def changed_sl_frame(self):
        if self.tabWidget.currentIndex() != 1:
            self.l_preview_image.setPixmap(update_preview(self.frames[self.sl_frame.value()], self.label_info()))

    def changed_sb_frames_count(self):
        if self.img:
            self.img = self.backup_img
            self.img = size_compensation(self.img,
                                         self.sb_vertical_line.value(),
                                         self.sb_horizontal_line.value()
                                         )
            self.frames.framesCount = self.sb_vertical_line.value(), self.sb_horizontal_line.value()
            self.frames.frameSize = self.img.size
            self.frames.__del__()
            divide_image(self.frames, self.img)
            self.sb_max_images.setMaximum(len(self.frames))
            self.sb_images_per_line.setMaximum(len(self.frames))
            self.sl_frame.setMaximum(len(self.frames)-1)
            self.sb_start_value.setMaximum(len(self.frames))
            self.sb_end_value.setMaximum(len(self.frames))
            self.l_preview_image.setPixmap(update_preview(self.frames[self.sl_frame.value()], self.label_info()))

    def label_info(self, mosaic=None):
        if mosaic:
            return self.txt_pattern.format(len(self.frames),
                                           "-",
                                           mosaic.size,
                                           mosaic.mode
                                           )
        else:
            return self.txt_pattern.format(len(self.frames),
                                           self.sl_frame.value()+1,
                                           self.frames[self.sl_frame.value()].size,
                                           self.frames[self.sl_frame.value()].mode
                                           )

    def render(self):
        filename = self.fld_filename.text() if self.fld_filename.text() else "frame"
        if self.cb_valid_frame_range.currentIndex() == 1:
            if self.sb_start_value.value() <= self.sb_end_value.value():
                for i in range(self.sb_start_value.value()-1, self.sb_end_value.value(), self.sb_inc_value.value()):
                    self.frames[i].save("{0}/{1}_{2}.{3}".format(
                        self.fld_out_path.text(),
                        filename,
                        i,
                        self.cb_image_format.currentText()
                    ))
                    print("{0}_{1} was saved".format(filename, i))
            else:
                self.statusbar.showMessage("Frame range is incorrect!", 3000)
        elif self.cb_valid_frame_range.currentIndex() == 0:
            self.frames[self.sl_frame.value()].save("{0}/{1}_{2}.{3}".format(
                self.fld_out_path.text(),
                filename,
                self.sl_frame.value(),
                self.cb_image_format.currentText()
            ))
            print("{0}_{1} was saved".format(filename, self.sl_frame.value()))
        elif self.cb_valid_frame_range.currentIndex() == 2:
            if self.frames.outMosaic:
                self.frames.outMosaic.save("{0}/{1}.{2}".format(
                    self.fld_out_path.text(),
                    filename,
                    self.cb_image_format.currentText()
                ))
                print("{0} was saved".format(filename))
            else:
                self.statusbar.showMessage("Mosaic is not created!", 3000)

    def closeEvent(self, event):
        messagebox = QMessageBox()
        messagebox.setIcon(QMessageBox.Question)
        icon = QIcon()
        icon.addPixmap(QPixmap(":/logo/icon.png"), QIcon.Normal, QIcon.Off)
        messagebox.setWindowIcon(icon)
        messagebox.setWindowTitle('Confirm Exit')
        messagebox.setText('Are you sure, you want to quit?')
        messagebox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        messagebox.setStyleSheet(
            "QLabel {color: rgb(203, 203, 203); }"
            "QMessageBox { background-color: rgb(81, 81, 81); }"
            "QPushButton { /* all types of tool button */\n"
            "    color: rgb(80, 80, 80);\n"
            "     border-left:1px solid rgb(75, 75, 75);\n"
            "    border-radius: 5px;\n"
            "    background-color: qlineargradient(spread:pad, x1:0.489045, y1:1, x2:0.472, y2:0, stop:0 rgba(111, 111, 111, 255), stop:1 rgba(155, 155, 155, 255));\n"
            "}\n"
            "QPushButton:pressed {\n"
            "    background-color: qlineargradient(spread:pad, x1:0.489045, y1:1, x2:0.472, y2:0, stop:0 rgba(158, 158, 158, 255), stop:1 rgba(203, 203, 203, 255));\n"
            "}\n"
            "QPushButton:hover {\n"
            "    background-color: qlineargradient(spread:pad, x1:0.489045, y1:1, x2:0.472, y2:0, stop:0 rgba(158, 158, 158, 255), stop:1 rgba(203, 203, 203, 255));\n"
            "}")
        buttonY = messagebox.button(QMessageBox.Yes)
        buttonN = messagebox.button(QMessageBox.No)
        buttonN.setFixedWidth(50)
        buttonY.setFixedWidth(50)
        buttonY.setFixedHeight(15)
        buttonN.setFixedHeight(15)
        res = messagebox.exec_()
        if res == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

def size_compensation(img, v_count, h_count):
    """Frames sizes must be an integer value, and that's bad if you are divide image.
    Sometimes, after divided we have float sizes. I calculated compensation for sizes.
    For example:
                My image have size 2048x2048, and frames count for vertical line/horizontal line is 10/21
                    1) 2048/10 = 204.8 and 2048/21 = 97.5238095, now my frame size is 204.8 x 97.5238095
                    It's wrong!!!
                    2) I must get remainder of the division.
                    204.8 % 1 = 0.8, 97.5238095 % 1 = 0.5238095
                    3) I must get a lack
                    1 - 0.8 = 0.2, 1 - 0.5238095 = 0.4761905 and multiply it to frames count
                    0.2 * 10 = 2, 0.4761905 * 21 = 10
                So, i got size compensation for image, it's 2 and 10, now i need add it to my image size
                2048 + 2 = 2050, 2048 + 10 = 2058, and resize it with new sizes.
    Now, if i will be divide image, i will get integer frame sizes 2050/10 = 205, 2058/21 = 98"""
    w, h = map(lambda x: int(((1 - (x[0]/x[1] % 1)) * x[1]) + x[0]) if x[0]/x[1] % 1 != 0 else x[0],
               zip(img.size, (v_count, h_count)))
    return img.resize((w, h), Image.ANTIALIAS)

def create_mosaic(fr, img_per_line, max_img, incr, color):

    frame_index_w = 0
    frame_index_h = 0
    w, h = fr[0].size
    max_img_temp = math.ceil(max_img / incr)
    kh = math.ceil(max_img_temp / img_per_line)
    kw = max_img_temp if max_img_temp < img_per_line else img_per_line
    background_img = Image.new('RGBA', (w * kw, h * kh), color)
    for i in range(0, max_img, incr):
        background_img.paste(fr[i], (frame_index_w * w, frame_index_h * h))
        frame_index_w += 1
        if frame_index_w == kw:
            frame_index_h += 1
            frame_index_w = 0
    fr.outMosaic = background_img
    return background_img

def divide_image(fr, img):
    left = 0
    top = 0
    right, bottom = fr.frameSize
    for j in range(1, fr.framesCount[1] + 1):
        if j >= 2:
            top = bottom
            bottom = fr.frameSize[1] * j
        for i in range(1, fr.framesCount[0] + 1):
            if i >= 2:
                left = right
                right = fr.frameSize[0] * i
            fr.framesList = img.crop((left, top, right, bottom))
        left = 0
        right = fr.frameSize[0]

def draw_text(img, txt):
    draw = ImageDraw.Draw(img)
    draw.text((12, 12), txt, font=ImageFont.load_default(), fill=(244, 168, 6, 255))

def update_preview(img, txt):
    background = Image.new('RGBA', (512, 512), (255, 255, 255, 0))
    info = Image.new('RGBA', (512, 512), (255, 255, 255, 0))
    img = img.resize(([x for x in map(lambda x: int(x / (max(img.size) / 512)), img.size)]), Image.ANTIALIAS)
    background.paste(img, [x for x in map(lambda x: round((x[0] - x[1]) / 2), zip(background.size, img.size))])
    draw_text(info, txt)
    img = Image.alpha_composite(background, info)

    if img.mode == "RGB":
        r, g, b = img.split()
        img = Image.merge("RGB", (b, g, r))
    elif img.mode == "RGBA":
        r, g, b, a = img.split()
        img = Image.merge("RGBA", (b, g, r, a))
    elif img.mode == "L":
        img = img.convert("RGBA")
    img = img.convert("RGBA")

    data = img.tobytes("raw", "RGBA")
    qim = QImage(data, img.width, img.height, QImage.Format_ARGB32)
    return QPixmap.fromImage(qim)

if __name__ == "__main__":
    qapp = QApplication(sys.argv)
    qapp.setWindowIcon(QIcon(":/logo/icon.png"))
    flipbook = Flipbook()
    flipbook.show()
    qapp.exec_()