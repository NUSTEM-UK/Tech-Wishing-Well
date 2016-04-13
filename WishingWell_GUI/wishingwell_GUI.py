from PyQt4 import QtCore, QtGui
import paho.mqtt.client as mqtt

# these modules allow us to convert a HSV colour value to a HEX code (via RGB)
import matplotlib.colors as colors
import colorsys

checkbox_status = True

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    
    
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1080, 720)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayoutWidget = QtGui.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(40, 100, 462, 432))
        self.gridLayoutWidget.setObjectName(_fromUtf8("gridLayoutWidget"))
        
        self.left_grid_layout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.left_grid_layout.setMargin(0)
        self.left_grid_layout.setObjectName(_fromUtf8("left_grid_layout"))

        self.servo_control_label = QtGui.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.servo_control_label.setFont(font)
        self.servo_control_label.setObjectName(_fromUtf8("servo_control_label"))
        self.left_grid_layout.addWidget(self.servo_control_label, 6, 0, 1, 1)
        
        self.colour_control_label = QtGui.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.colour_control_label.setFont(font)
        self.colour_control_label.setObjectName(_fromUtf8("colour_control_label"))
        self.left_grid_layout.addWidget(self.colour_control_label, 6, 1, 1, 1)
        
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.left_grid_layout.addItem(spacerItem, 5, 1, 1, 1)
        
        self.scut3 = QtGui.QCheckBox(self.gridLayoutWidget)
        self.scut3.setObjectName(_fromUtf8("scut3"))
        self.left_grid_layout.addWidget(self.scut3, 1, 2, 1, 1)
        
        self.vertical_layout_colour = QtGui.QVBoxLayout()
        self.vertical_layout_colour.setObjectName(_fromUtf8("vertical_layout_colour"))
        
        self.brightness_label = QtGui.QLabel(self.gridLayoutWidget)
        self.brightness_label.setObjectName(_fromUtf8("brightness_label"))
        
        self.vertical_layout_colour.addWidget(self.brightness_label)
        self.bright_slider = QtGui.QSlider(self.gridLayoutWidget)
        self.bright_slider.setOrientation(QtCore.Qt.Horizontal)
        self.bright_slider.setObjectName(_fromUtf8("bright_slider"))
        self.vertical_layout_colour.addWidget(self.bright_slider)
        self.hue_label = QtGui.QLabel(self.gridLayoutWidget)
        self.hue_label.setObjectName(_fromUtf8("hue_label"))
        self.vertical_layout_colour.addWidget(self.hue_label)
        
        self.hue_slider = QtGui.QSlider(self.gridLayoutWidget)
        self.hue_slider.setOrientation(QtCore.Qt.Horizontal)
        self.hue_slider.setObjectName(_fromUtf8("hue_slider"))
        self.vertical_layout_colour.addWidget(self.hue_slider)
        
        self.colour_display = QtGui.QFrame(self.gridLayoutWidget)
        self.colour_display.setFrameShape(QtGui.QFrame.StyledPanel)
        self.colour_display.setFrameShadow(QtGui.QFrame.Raised)
        self.colour_display.setObjectName(_fromUtf8("colour_display"))
        
        self.vertical_layout_colour.addWidget(self.colour_display)
        self.left_grid_layout.addLayout(self.vertical_layout_colour, 7, 1, 1, 1)
        
        self.scut4 = QtGui.QCheckBox(self.gridLayoutWidget)
        self.scut4.setObjectName(_fromUtf8("scut4"))
        self.left_grid_layout.addWidget(self.scut4, 1, 3, 1, 1)
        
        self.scut9 = QtGui.QCheckBox(self.gridLayoutWidget)
        self.scut9.setObjectName(_fromUtf8("scut9"))
        self.left_grid_layout.addWidget(self.scut9, 3, 0, 1, 1)
        
        self.scut1 = QtGui.QCheckBox(self.gridLayoutWidget)
        self.scut1.setObjectName(_fromUtf8("scut1"))
        self.left_grid_layout.addWidget(self.scut1, 1, 0, 1, 1)
        self.vertical_layout_wheel = QtGui.QVBoxLayout()
        self.vertical_layout_wheel.setObjectName(_fromUtf8("vertical_layout_wheel"))
        self.trans_wheel = QtGui.QRadioButton(self.gridLayoutWidget)
        self.trans_wheel.setObjectName(_fromUtf8("trans_wheel"))
        self.vertical_layout_wheel.addWidget(self.trans_wheel)
        self.tran_fade = QtGui.QRadioButton(self.gridLayoutWidget)
        self.tran_fade.setObjectName(_fromUtf8("tran_fade"))
        self.vertical_layout_wheel.addWidget(self.tran_fade)
        self.left_grid_layout.addLayout(self.vertical_layout_wheel, 7, 2, 1, 1)
        self.scut6 = QtGui.QCheckBox(self.gridLayoutWidget)
        self.scut6.setObjectName(_fromUtf8("scut6"))
        self.left_grid_layout.addWidget(self.scut6, 2, 1, 1, 1)
        self.scut2 = QtGui.QCheckBox(self.gridLayoutWidget)
        self.scut2.setObjectName(_fromUtf8("scut2"))
        self.left_grid_layout.addWidget(self.scut2, 1, 1, 1, 1)
        self.scut5 = QtGui.QCheckBox(self.gridLayoutWidget)
        self.scut5.setObjectName(_fromUtf8("scut5"))
        self.left_grid_layout.addWidget(self.scut5, 2, 0, 1, 1)
        self.scut7 = QtGui.QCheckBox(self.gridLayoutWidget)
        self.scut7.setObjectName(_fromUtf8("scut7"))
        self.left_grid_layout.addWidget(self.scut7, 2, 2, 1, 1)
        self.scut10 = QtGui.QCheckBox(self.gridLayoutWidget)
        self.scut10.setObjectName(_fromUtf8("scut10"))
        self.left_grid_layout.addWidget(self.scut10, 3, 1, 1, 1)
        self.scut8 = QtGui.QCheckBox(self.gridLayoutWidget)
        self.scut8.setObjectName(_fromUtf8("scut8"))
        self.left_grid_layout.addWidget(self.scut8, 2, 3, 1, 1)
        self.scutter_control_label = QtGui.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.scutter_control_label.setFont(font)
        self.scutter_control_label.setScaledContents(True)
        self.scutter_control_label.setObjectName(_fromUtf8("scutter_control_label"))
        self.left_grid_layout.addWidget(self.scutter_control_label, 0, 0, 1, 1)
        
        # vertical layout for the servo control
        self.vertical_layout_servo = QtGui.QVBoxLayout()
        self.vertical_layout_servo.setObjectName(_fromUtf8("vertical_layout_servo"))
        
        # the servo dial and LCD setup
        self.servo_dial = QtGui.QDial(self.gridLayoutWidget)
        self.servo_dial.setNotchesVisible(True)
        self.servo_dial.setObjectName(_fromUtf8("servo_dial"))
        self.vertical_layout_servo.addWidget(self.servo_dial)
        
        self.servo_display = QtGui.QLCDNumber(self.gridLayoutWidget)
        self.servo_display.setObjectName(_fromUtf8("servo_display"))
        self.vertical_layout_servo.addWidget(self.servo_display)
        self.left_grid_layout.addLayout(self.vertical_layout_servo, 7, 0, 1, 1)
        
        # vertical layout for transition time
        self.vertical_layout_time = QtGui.QVBoxLayout()
        self.vertical_layout_time.setObjectName(_fromUtf8("vertical_layout_time"))
        
        
        self.trans_time_label = QtGui.QLabel(self.gridLayoutWidget)
        self.trans_time_label.setObjectName(_fromUtf8("trans_time_label"))
        self.vertical_layout_time.addWidget(self.trans_time_label)
        self.trans_time = QtGui.QSpinBox(self.gridLayoutWidget)
        self.trans_time.setObjectName(_fromUtf8("trans_time"))
        self.vertical_layout_time.addWidget(self.trans_time)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.vertical_layout_time.addItem(spacerItem1)
        self.left_grid_layout.addLayout(self.vertical_layout_time, 7, 3, 1, 1)
        self.scut_update = QtGui.QPushButton(self.gridLayoutWidget)
        self.scut_update.setObjectName(_fromUtf8("scut_update"))
        self.left_grid_layout.addWidget(self.scut_update, 9, 3, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.left_grid_layout.addItem(spacerItem2, 8, 3, 1, 1)
        self.scut_toggle = QtGui.QPushButton(self.gridLayoutWidget)
        self.scut_toggle.setObjectName(_fromUtf8("scut_toggle"))
        self.left_grid_layout.addWidget(self.scut_toggle, 4, 3, 1, 1)
        self.gridLayoutWidget_2 = QtGui.QWidget(self.centralwidget)
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(740, 100, 191, 401))
        self.gridLayoutWidget_2.setObjectName(_fromUtf8("gridLayoutWidget_2"))
        self.right_grid_layout = QtGui.QGridLayout(self.gridLayoutWidget_2)
        self.right_grid_layout.setMargin(0)
        self.right_grid_layout.setObjectName(_fromUtf8("right_grid_layout"))
        
        self.wishing_label_5 = QtGui.QLabel(self.gridLayoutWidget_2)
        self.wishing_label_5.setObjectName(_fromUtf8("wishing_label_5"))
        self.right_grid_layout.addWidget(self.wishing_label_5, 5, 1, 1, 1)
        self.wishing_display_2 = QtGui.QLCDNumber(self.gridLayoutWidget_2)
        self.wishing_display_2.setObjectName(_fromUtf8("wishing_display_2"))
        self.right_grid_layout.addWidget(self.wishing_display_2, 2, 2, 1, 1)
        self.wishing_display_7 = QtGui.QLCDNumber(self.gridLayoutWidget_2)
        self.wishing_display_7.setObjectName(_fromUtf8("wishing_display_7"))
        self.right_grid_layout.addWidget(self.wishing_display_7, 7, 2, 1, 1)
        self.wishing_label_4 = QtGui.QLabel(self.gridLayoutWidget_2)
        self.wishing_label_4.setObjectName(_fromUtf8("wishing_label_4"))
        self.right_grid_layout.addWidget(self.wishing_label_4, 4, 1, 1, 1)
        self.wishing_display_5 = QtGui.QLCDNumber(self.gridLayoutWidget_2)
        self.wishing_display_5.setObjectName(_fromUtf8("wishing_display_5"))
        self.right_grid_layout.addWidget(self.wishing_display_5, 5, 2, 1, 1)
        self.wishing_well_label = QtGui.QLabel(self.gridLayoutWidget_2)
        font = QtGui.QFont()
        font.setBold(True)
        font.setUnderline(False)
        font.setWeight(75)
        self.wishing_well_label.setFont(font)
        self.wishing_well_label.setObjectName(_fromUtf8("wishing_well_label"))
        self.right_grid_layout.addWidget(self.wishing_well_label, 0, 1, 1, 1)
        self.wishing_display_6 = QtGui.QLCDNumber(self.gridLayoutWidget_2)
        self.wishing_display_6.setObjectName(_fromUtf8("wishing_display_6"))
        self.right_grid_layout.addWidget(self.wishing_display_6, 6, 2, 1, 1)
        self.wishing_label_2 = QtGui.QLabel(self.gridLayoutWidget_2)
        self.wishing_label_2.setObjectName(_fromUtf8("wishing_label_2"))
        self.right_grid_layout.addWidget(self.wishing_label_2, 2, 1, 1, 1)
        self.wishing_label_6 = QtGui.QLabel(self.gridLayoutWidget_2)
        self.wishing_label_6.setObjectName(_fromUtf8("wishing_label_6"))
        self.right_grid_layout.addWidget(self.wishing_label_6, 6, 1, 1, 1)
        self.wishing_label_3 = QtGui.QLabel(self.gridLayoutWidget_2)
        self.wishing_label_3.setObjectName(_fromUtf8("wishing_label_3"))
        self.right_grid_layout.addWidget(self.wishing_label_3, 3, 1, 1, 1)
        self.wishing_display_3 = QtGui.QLCDNumber(self.gridLayoutWidget_2)
        self.wishing_display_3.setObjectName(_fromUtf8("wishing_display_3"))
        self.right_grid_layout.addWidget(self.wishing_display_3, 3, 2, 1, 1)
        self.wishing_display_1 = QtGui.QLCDNumber(self.gridLayoutWidget_2)
        self.wishing_display_1.setObjectName(_fromUtf8("wishing_display_1"))
        self.right_grid_layout.addWidget(self.wishing_display_1, 1, 2, 1, 1)
        self.wishing_label_1 = QtGui.QLabel(self.gridLayoutWidget_2)
        self.wishing_label_1.setObjectName(_fromUtf8("wishing_label_1"))
        self.right_grid_layout.addWidget(self.wishing_label_1, 1, 1, 1, 1)
        self.wishing_label_7 = QtGui.QLabel(self.gridLayoutWidget_2)
        self.wishing_label_7.setObjectName(_fromUtf8("wishing_label_7"))
        self.right_grid_layout.addWidget(self.wishing_label_7, 7, 1, 1, 1)
        self.wishing_display_4 = QtGui.QLCDNumber(self.gridLayoutWidget_2)
        self.wishing_display_4.setObjectName(_fromUtf8("wishing_display_4"))
        self.right_grid_layout.addWidget(self.wishing_display_4, 4, 2, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1080, 27))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.clockwise = QtGui.QRadioButton(self.gridLayoutWidget)
        self.clockwise.setObjectName(_fromUtf8("clockwise"))
        self.left_grid_layout.addWidget(self.clockwise, 8, 0, 1, 1)
        self.anticlockwise = QtGui.QRadioButton(self.gridLayoutWidget)
        self.anticlockwise.setObjectName(_fromUtf8("anticlockwise"))
        self.left_grid_layout.addWidget(self.anticlockwise, 9, 0, 1, 1)
        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.servo_dial, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), self.servo_display.display)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
        #button clicked controls for the various buttons and checkboxes on the GUI
        # Select All / None button
        self.scut_toggle.clicked.connect(self.scut_toggler)
        
        # Send update button
        self.scut_update.clicked.connect(self.scutter_update)
                        
        # hue slider
        self.hue_slider.sliderReleased.connect(self.HSVtoHEXupload) 
        
        # brightness slider
        self.bright_slider.sliderReleased.connect(self.HSVtoHEXupload) 
               
    def scut_toggler(self):
        self.scut1.setChecked(True)
        global checkbox_status
        if checkbox_status == False:
            self.scut1.setChecked(True)
            self.scut2.setChecked(True)
            self.scut3.setChecked(True)
            self.scut4.setChecked(True)
            self.scut5.setChecked(True)
            self.scut6.setChecked(True)
            self.scut7.setChecked(True)
            self.scut8.setChecked(True)
            self.scut9.setChecked(True)
            self.scut10.setChecked(True)
            checkbox_status = True
        else:
            self.scut1.setChecked(False)
            self.scut2.setChecked(False)
            self.scut3.setChecked(False)
            self.scut4.setChecked(False)
            self.scut5.setChecked(False)
            self.scut6.setChecked(False)
            self.scut7.setChecked(False)
            self.scut8.setChecked(False)
            self.scut9.setChecked(False)
            self.scut10.setChecked(False)
            checkbox_status = False
            
    def scutter_update(self):
        print "Connecting to the MQTT"
        print "Publishing scutter update codes..."
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/Scutter_18:FE:34:F4:D6:F4", self.scut1.isChecked())
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/Scutter_18:FE:34:F4:D4:79", self.scut2.isChecked())
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/Scutter_5C:CF:7F:0E:2C:EA", self.scut3.isChecked())
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/Scutter_5C:CF:7F:01:59:76", self.scut4.isChecked())
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/Scutter_18:FE:34:F4:D3:BD", self.scut5.isChecked())
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/Scutter_5C:CF:7F:01:59:5B", self.scut6.isChecked())
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/Scutter_5C:CF:7F:0E:35:2D", self.scut7.isChecked())
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/Scutter_18:FE:34:FD:92:D1", self.scut8.isChecked())
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/Scutter_5C:CF:7F:0E:31:16", self.scut9.isChecked())
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/scutter/Scutter_18:FE:34:F4:D0:7B", self.scut10.checkState())
        print "Update complete."
        print "Publishing current settings"
        self.settings_update()
        
    def settings_update(self):
        # publish the servo speed
        print "Publishing new servo speed: %s" % self.servo_dial.value()
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/speed", self.servo_dial.value())
        
        # publish the time for the colour changed
        print "Publishing new colour change time: %s" % self.trans_time.value()
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/time", self.trans_time.value())
        
        # publish the current hex colour
        s = 1
        v = self.bright_slider.value() /100.0
        h = self.hue_slider.value() / 100.0
            # convert the HSV to RGB
        rgb_colours = colorsys.hsv_to_rgb(h,s,v)
            #convert the RGB to HEX
        hex_colour = colors.rgb2hex((rgb_colours[0], rgb_colours[1], rgb_colours[2]))
        print "Publishing new colour change colour: %s" % hex_colour
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/colour", hex_colour)
        
        # publsih the radio value for the fade or wheel
        print "Trans/wheel?? %s" % self.trans_wheel.isChecked()
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        if self.trans_wheel.isChecked() == True:
            mqttc.publish("wishing/transition", "Wheel")
        else:
            mqttc.publish("wishing/transition", "fade")
        
    def HSVtoHEXupload(self):
        s = 1
        v = self.bright_slider.value() /100.0
        h = self.hue_slider.value() / 100.0
        # convert the HSV to RGB
        rgb_colours = colorsys.hsv_to_rgb(h,s,v)
        
        #convert the RGB to HEX
        hex_colour = colors.rgb2hex((rgb_colours[0], rgb_colours[1], rgb_colours[2]))
        print hex_colour
        
        # and update the colour frame on the GUI
        self.colour_display.setStyleSheet("QFrame { background-color: %s}" % hex_colour)
    
    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.servo_control_label.setText(_translate("MainWindow", "Servo Control", None))
        self.colour_control_label.setText(_translate("MainWindow", "Colour Control", None))
        self.scut3.setText(_translate("MainWindow", "Scutter 3", None))
        self.brightness_label.setText(_translate("MainWindow", "Brightness", None))
        self.hue_label.setText(_translate("MainWindow", "Hue", None))
        self.scut4.setText(_translate("MainWindow", "Scutter 4", None))
        self.scut9.setText(_translate("MainWindow", "Scutter 9", None))
        self.scut1.setText(_translate("MainWindow", "Scutter 1", None))
        self.trans_wheel.setText(_translate("MainWindow", "Wheel", None))
        self.tran_fade.setText(_translate("MainWindow", "Fade", None))
        self.scut6.setText(_translate("MainWindow", "Scutter 6", None))
        self.scut2.setText(_translate("MainWindow", "Scutter 2", None))
        self.scut5.setText(_translate("MainWindow", "Scutter 5", None))
        self.scut7.setText(_translate("MainWindow", "Scutter 7", None))
        self.scut10.setText(_translate("MainWindow", "Scutter 10", None))
        self.scut8.setText(_translate("MainWindow", "Scutter 8", None))
        self.scutter_control_label.setText(_translate("MainWindow", "Scutter Control", None))
        self.trans_time_label.setText(_translate("MainWindow", "Time (seconds)", None))
        self.scut_update.setText(_translate("MainWindow", "Send Update", None))
        self.scut_toggle.setText(_translate("MainWindow", "Select All/None", None))
        self.wishing_label_5.setText(_translate("MainWindow", "TextLabel", None))
        self.wishing_label_4.setText(_translate("MainWindow", "TextLabel", None))
        self.wishing_well_label.setText(_translate("MainWindow", "Wishing Well", None))
        self.wishing_label_2.setText(_translate("MainWindow", "TextLabel", None))
        self.wishing_label_6.setText(_translate("MainWindow", "TextLabel", None))
        self.wishing_label_3.setText(_translate("MainWindow", "TextLabel", None))
        self.wishing_label_1.setText(_translate("MainWindow", "TextLabel", None))
        self.wishing_label_7.setText(_translate("MainWindow", "TextLabel", None))
        self.clockwise.setText(_translate("MainWindow", "Clockwise", None))
        self.anticlockwise.setText(_translate("MainWindow", "Anticlockwise", None))

if __name__ == "__main__":
    import sys

    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    
    sys.exit(app.exec_())

