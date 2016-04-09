
from PyQt4 import QtCore, QtGui
import paho.mqtt.client as mqtt

# these modules allow us to convert a HSV colour value to a HEX code (via RGB)
import matplotlib.colors as colors
import colorsys

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
        
        # this code sets the main attributes of the window
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(640, 480)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayoutWidget = QtGui.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(20, 20, 313, 331))
        self.gridLayoutWidget.setObjectName(_fromUtf8("gridLayoutWidget"))
        self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_3 = QtGui.QLabel(self.gridLayoutWidget)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 4, 3, 1, 1)
        self.label_2 = QtGui.QLabel(self.gridLayoutWidget)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 4, 2, 1, 1)
        
        # Scutter 1 Setup
        self.scut1 = QtGui.QCheckBox(self.gridLayoutWidget)
        self.scut1.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.scut1.setObjectName(_fromUtf8("scut1"))
        self.gridLayout.addWidget(self.scut1, 0, 0, 1, 1)
        
        # Scutter 2 Setup
        self.scut2 = QtGui.QCheckBox(self.gridLayoutWidget)
        self.scut2.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.scut2.setObjectName(_fromUtf8("scut2"))
        self.gridLayout.addWidget(self.scut2, 0, 2, 1, 1)
        
        # Scutter 3 Setup
        self.scut3 = QtGui.QCheckBox(self.gridLayoutWidget)
        self.scut3.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.scut3.setObjectName(_fromUtf8("scut3"))
        self.gridLayout.addWidget(self.scut3, 0, 3, 1, 1)
        
        # Scutter 4 Setup
        self.scut4 = QtGui.QCheckBox(self.gridLayoutWidget)
        self.scut4.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.scut4.setObjectName(_fromUtf8("scut4"))
        self.gridLayout.addWidget(self.scut4, 1, 0, 1, 1)
        
        # Scutter 5 Setup
        self.scut5 = QtGui.QCheckBox(self.gridLayoutWidget)
        self.scut5.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.scut5.setObjectName(_fromUtf8("scut5"))
        self.gridLayout.addWidget(self.scut5, 1, 2, 1, 1)

        # Scutter 6 Setup
        self.scut6 = QtGui.QCheckBox(self.gridLayoutWidget)
        self.scut6.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.scut6.setObjectName(_fromUtf8("scut6"))
        self.gridLayout.addWidget(self.scut6, 1, 3, 1, 1)
        
        # Scutter 7 Setup
        self.scut7 = QtGui.QCheckBox(self.gridLayoutWidget)
        self.scut7.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.scut7.setObjectName(_fromUtf8("scut7"))
        self.gridLayout.addWidget(self.scut7, 2, 0, 1, 1)
        
        # Scutter 8 Setup
        self.scut8 = QtGui.QCheckBox(self.gridLayoutWidget)
        self.scut8.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.scut8.setObjectName(_fromUtf8("scut8"))
        self.gridLayout.addWidget(self.scut8, 2, 2, 1, 1)
        
        # Scutter 9 Setup
        self.scut9 = QtGui.QCheckBox(self.gridLayoutWidget)
        self.scut9.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.scut9.setObjectName(_fromUtf8("scut9"))
        self.gridLayout.addWidget(self.scut9, 2, 3, 1, 1)
        
        # send_update button
        self.send_update = QtGui.QPushButton(self.gridLayoutWidget)
        self.send_update.setObjectName(_fromUtf8("send_update"))
        self.gridLayout.addWidget(self.send_update, 7, 2, 1, 1)
        
        # when the button is clicked, run the self.scutter_update
        self.send_update.clicked.connect(self.scutter_update)
    
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 3, 2, 1, 1)
        
        # Hue slider setup
        self.hue_slider = QtGui.QSlider(self.gridLayoutWidget)
        self.hue_slider.setMaximum(255)
        self.hue_slider.setOrientation(QtCore.Qt.Horizontal)
        self.hue_slider.setObjectName(_fromUtf8("hue_slider"))
        self.gridLayout.addWidget(self.hue_slider, 5, 2, 1, 1)
        
        self.hue_slider.sliderReleased.connect(self.HSVtoHEXupload) # connect the slider to colour function
        
        # Servo LCD setup
        self.servo_num = QtGui.QLCDNumber(self.gridLayoutWidget)
        self.servo_num.setObjectName(_fromUtf8("servo_num"))
        self.gridLayout.addWidget(self.servo_num, 6, 0, 1, 1)
        
        self.label = QtGui.QLabel(self.gridLayoutWidget)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 4, 0, 1, 1)
        
        # Servo Speed dial setup
        self.speed_dial = QtGui.QDial(self.gridLayoutWidget)
        self.speed_dial.setCursor(QtGui.QCursor(QtCore.Qt.ClosedHandCursor))
        self.speed_dial.setMaximum(100)
        self.speed_dial.setInvertedControls(False)
        self.speed_dial.setWrapping(False)
        self.speed_dial.setNotchesVisible(True)
        self.speed_dial.setObjectName(_fromUtf8("speed_dial"))
        self.gridLayout.addWidget(self.speed_dial, 5, 0, 1, 1)
        
        self.speed_dial.sliderReleased.connect(self.speed_update)   #connect the speed slider to the speed_update function
        
        # Brightness LCD setup
        self.bright_num = QtGui.QLCDNumber(self.gridLayoutWidget)
        self.bright_num.setObjectName(_fromUtf8("bright_num"))
        self.gridLayout.addWidget(self.bright_num, 6, 3, 1, 1)
        
        # Brightness slider setup
        self.bright_slider = QtGui.QSlider(self.gridLayoutWidget)
        self.bright_slider.setMaximum(100)
        self.bright_slider.setOrientation(QtCore.Qt.Horizontal)
        self.bright_slider.setObjectName(_fromUtf8("bright_slider"))
        self.gridLayout.addWidget(self.bright_slider, 5, 3, 1, 1)
        
        self.bright_slider.sliderReleased.connect(self.HSVtoHEXupload)  #connect the brightness slider to the colour update function
        
        # Colour frame display setup
        self.colourframe = QtGui.QFrame(self.gridLayoutWidget)
        self.colourframe.setFrameShape(QtGui.QFrame.StyledPanel)
        self.colourframe.setFrameShadow(QtGui.QFrame.Raised)
        self.colourframe.setObjectName(_fromUtf8("colourframe"))
        self.gridLayout.addWidget(self.colourframe, 6, 2, 1, 1)
        
        # menu bar setup
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 640, 27))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        
        # connect the sliders to their respective LCD dials
        QtCore.QObject.connect(self.bright_slider, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), self.bright_num.display)
        QtCore.QObject.connect(self.speed_dial, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), self.servo_num.display)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
    def scutter_update(self):
        print "Connecting to the MQTT"
        print "Publishing scutter update codes..."
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/Scutter_18:FE:34:F4:D6:F4", self.scut1.checkState())
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/Scutter_18:FE:34:F4:D4:79", self.scut2.checkState())
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/Scutter_5C:CF:7F:0E:2C:EA", self.scut3.checkState())
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/Scutter_5C:CF:7F:01:59:76", self.scut4.checkState())
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/Scutter_18:FE:34:F4:D3:BD", self.scut5.checkState())
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/Scutter_5C:CF:7F:01:59:5B", self.scut6.checkState())
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/Scutter_5C:CF:7F:0E:35:2D", self.scut7.checkState())
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/Scutter_18:FE:34:FD:92:D1", self.scut8.checkState())
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/Scutter_5C:CF:7F:0E:31:16", self.scut9.checkState())
        print "Update complete."
        #mqttc.publish("wishing/scutter/Scutter_18:FE:34:F4:D0:7B", self.scut10.checkState())
        
    def HSVtoHEXupload(self):
        s = 1
        v = self.bright_slider.value() /100
        h = self.hue_slider.value() / 100
        
        # convert the HSV to RGB
        rgb_colours = colorsys.hsv_to_rgb(h,s,v)
        
        #convert the RGB to HEX
        hex_colour = colors.rgb2hex((rgb_colours[0], rgb_colours[1], rgb_colours[2]))
        
        # now publish the colour code to MQTT
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/colour", hex_colour)
        
        # and update the colour frame on the GUI
            
    def speed_update(self):
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/speed", self.speed_dial.value())
        
    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.label_3.setText(_translate("MainWindow", "Brightness", None))
        self.label_2.setText(_translate("MainWindow", "Hue", None))
        self.scut5.setText(_translate("MainWindow", "Scutter 5", None))
        self.scut1.setText(_translate("MainWindow", "Scutter 1", None))
        self.scut6.setText(_translate("MainWindow", "Scutter 6", None))
        self.scut8.setText(_translate("MainWindow", "Scutter 8", None))
        self.scut9.setText(_translate("MainWindow", "Scutter 9", None))
        self.scut4.setText(_translate("MainWindow", "Scutter 4", None))
        self.scut7.setText(_translate("MainWindow", "Scutter 7", None))
        self.scut2.setText(_translate("MainWindow", "Scutter 2", None))
        self.scut3.setText(_translate("MainWindow", "Scutter 3", None))
        self.send_update.setText(_translate("MainWindow", "Send Update", None))
        self.label.setText(_translate("MainWindow", "Servo Speed", None))

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

