##############################################################################
# This code outputs data from the GUI to the following MQTT topics on        #
# 'localhost', port '1883'                                                   #
#                                                                            #
#   Topic/Subtopic                      Values                               #
#   wishing/scutter_MAC_ADDRESS         bool True / False                    #
#   Wishing/speed                       int 0 - 100                          #
#   wishing/colour                      hex colour code                      #
#   wishing/time                        int >= 0                             #
#   wishing/transition                  wheel / fade                         #
#   wishing/direction                   forwards / reverse                   #
#                                                                            #
##############################################################################

from PyQt4 import QtCore, QtGui
#import paho.mqtt.client as mqtt

# these modules allow us to convert a HSV colour value to a HEX code (via RGB)
import matplotlib.colors as colors
import colorsys

# These next lines of code will eventually allow for easier input of MQTT server location and port
# they are not yet connected to any functions within the code
# host = 'locahost'
# port = 1883
# client_label = 'python_pub'   # this provides a reference on the MQTT server as to which entity published the data, in our case the GUI

checkbox_status = True

# unsure what this bit does, but if you take it out... codey no worky.

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
    
    # lines 51 - 269 are concerned with setting out the layout of the window and the 
    # various QObjects held within it, useful code with which to change inputs and outputs can
    # be found from line 274 onwards
    
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(540, 500)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayoutWidget = QtGui.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(40, 20, 462, 432))
        self.gridLayoutWidget.setObjectName(_fromUtf8("gridLayoutWidget"))
        
        # setup the grid that all the objects will be placed within
        self.left_grid_layout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.left_grid_layout.setMargin(0)
        self.left_grid_layout.setObjectName(_fromUtf8("left_grid_layout"))
        
        # this group box confine the wheel/fade radio checkboxes
        self.groupBox = QtGui.QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(_fromUtf8("colourgroup"))
        # give the group an invisible background (default is a shade of grey
        self.groupBox.setFlat(True)
        # put the group into the correct position in the grid layout
        self.left_grid_layout.addWidget(self.groupBox, 7, 2, 1, 1)
		
		# this group box confine the wheel/fade radio checkboxes
        self.groupBox2 = QtGui.QGroupBox(self.centralwidget)
        self.groupBox2.setObjectName(_fromUtf8("directiongroup"))
        self.groupBox2.setFlat(True)
        self.left_grid_layout.addWidget(self.groupBox2, 8, 0, 1, 1)
        
        # PyQT4 code for the Skutter Checkboxes
        # Step 1 - define the QCheckbox as part of the self.gridLayoutWidget
        # Step 2 - name the QCheckbox
        # Step 3 - place the checkbox in the correct row and column in the left_grid_layout
        # create the checkbox
        self.skut1 = QtGui.QCheckBox(self.gridLayoutWidget)
        # name the checkbox
        self.skut1.setObjectName(_fromUtf8("skut1"))
        # place the checkbox
        self.left_grid_layout.addWidget(self.skut1, 1, 0, 1, 1)
        
        self.skut2 = QtGui.QCheckBox(self.gridLayoutWidget)
        self.skut2.setObjectName(_fromUtf8("skut2"))
        self.left_grid_layout.addWidget(self.skut2, 1, 1, 1, 1)
        
        self.skut3 = QtGui.QCheckBox(self.gridLayoutWidget)
        self.skut3.setObjectName(_fromUtf8("skut3"))
        self.left_grid_layout.addWidget(self.skut3, 1, 2, 1, 1)
        
        self.skut4 = QtGui.QCheckBox(self.gridLayoutWidget)
        self.skut4.setObjectName(_fromUtf8("skut4"))
        self.left_grid_layout.addWidget(self.skut4, 2, 0, 1, 1)
        
        self.skut5 = QtGui.QCheckBox(self.gridLayoutWidget)
        self.skut5.setObjectName(_fromUtf8("skut5"))
        self.left_grid_layout.addWidget(self.skut5, 2, 1, 1, 1)
        
        self.skut6 = QtGui.QCheckBox(self.gridLayoutWidget)
        self.skut6.setObjectName(_fromUtf8("skut6"))
        self.left_grid_layout.addWidget(self.skut6, 2, 2, 1, 1)
        
        self.skut7 = QtGui.QCheckBox(self.gridLayoutWidget)
        self.skut7.setObjectName(_fromUtf8("skut7"))
        self.left_grid_layout.addWidget(self.skut7, 3, 0, 1, 1)
        
        self.skut8 = QtGui.QCheckBox(self.gridLayoutWidget)
        self.skut8.setObjectName(_fromUtf8("skut8"))
        self.left_grid_layout.addWidget(self.skut8, 3, 1, 1, 1)
        
        self.skut9 = QtGui.QCheckBox(self.gridLayoutWidget)
        self.skut9.setObjectName(_fromUtf8("skut9"))
        self.left_grid_layout.addWidget(self.skut9, 3, 2, 1, 1)
        
        
		# Add the bold label for the servo control
        self.servo_control_label = QtGui.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.servo_control_label.setFont(font)
        self.servo_control_label.setObjectName(_fromUtf8("servo_control_label"))
        self.left_grid_layout.addWidget(self.servo_control_label, 6, 0, 1, 1)
        
        # add the bold label for the colour control
        self.colour_control_label = QtGui.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.colour_control_label.setFont(font)
        self.colour_control_label.setObjectName(_fromUtf8("colour_control_label"))
        self.left_grid_layout.addWidget(self.colour_control_label, 6, 1, 1, 1)
        
        #spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        #self.left_grid_layout.addItem(spacerItem, 5, 1, 1, 1)
        
        # create a vertical layout to go within the grid to hold the hue and brightness sliders
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
        
        
        
        
        self.vertical_layout_wheel = QtGui.QVBoxLayout(self.groupBox)
        self.vertical_layout_wheel.setObjectName(_fromUtf8("vertical_layout_wheel"))
        self.trans_wheel = QtGui.QRadioButton(self.gridLayoutWidget)
        self.trans_wheel.setObjectName(_fromUtf8("trans_wheel"))
        self.vertical_layout_wheel.addWidget(self.trans_wheel)
        self.tran_fade = QtGui.QRadioButton(self.gridLayoutWidget)
        self.tran_fade.setObjectName(_fromUtf8("tran_fade"))
        self.vertical_layout_wheel.addWidget(self.tran_fade)
        self.trans_wheel.setChecked(True)
        #self.left_grid_layout.addLayout(self.vertical_layout_wheel, 7, 2, 1, 1)
        
        
        self.vertical_layout_direction = QtGui.QVBoxLayout(self.groupBox2)
        self.vertical_layout_direction.setObjectName(_fromUtf8("vertical_layout_direction"))
		
	self.clockwise = QtGui.QRadioButton(self.gridLayoutWidget)
        self.clockwise.setObjectName(_fromUtf8("clockwise"))
        self.vertical_layout_direction.addWidget(self.clockwise)
        self.anticlockwise = QtGui.QRadioButton(self.gridLayoutWidget)
        self.anticlockwise.setObjectName(_fromUtf8("anticlockwise"))
        self.vertical_layout_direction.addWidget(self.anticlockwise)
        self.clockwise.setChecked(True)

        
        self.skutter_control_label = QtGui.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.skutter_control_label.setFont(font)
        self.skutter_control_label.setScaledContents(True)
        self.skutter_control_label.setObjectName(_fromUtf8("skutter_control_label"))
        self.left_grid_layout.addWidget(self.skutter_control_label, 0, 0, 1, 1)
        
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
        
        # add the label for the transition time QSpinBox
        self.trans_time_label = QtGui.QLabel(self.gridLayoutWidget)
        self.trans_time_label.setObjectName(_fromUtf8("trans_time_label"))
        self.vertical_layout_time.addWidget(self.trans_time_label)
        
        # add the transition time QSpinBox to the vertical layout within the grid
        self.trans_time = QtGui.QSpinBox(self.gridLayoutWidget)
        self.trans_time.setObjectName(_fromUtf8("trans_time"))
        self.vertical_layout_time.addWidget(self.trans_time)
        
        #spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        #self.vertical_layout_time.addItem(spacerItem1)
        
        self.left_grid_layout.addLayout(self.vertical_layout_time, 7, 3, 1, 1)
        self.skut_update = QtGui.QPushButton(self.gridLayoutWidget)
        self.skut_update.setObjectName(_fromUtf8("skut_update"))
        self.left_grid_layout.addWidget(self.skut_update, 9, 3, 1, 1)
        
       # spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        #self.left_grid_layout.addItem(spacerItem2, 8, 3, 1, 1)
        
        self.skut_toggle = QtGui.QPushButton(self.gridLayoutWidget)
        self.skut_toggle.setObjectName(_fromUtf8("skut_toggle"))
        self.skut_toggle.setFixedSize(80, 30)
        self.left_grid_layout.addWidget(self.skut_toggle, 4, 3, 1, 1)
        """
        self.gridLayoutWidget_2 = QtGui.QWidget(self.centralwidget)
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(740, 100, 191, 401))
        self.gridLayoutWidget_2.setObjectName(_fromUtf8("gridLayoutWidget_2"))
        
        self.right_grid_layout = QtGui.QGridLayout(self.gridLayoutWidget_2)
        self.right_grid_layout.setMargin(0)
        self.right_grid_layout.setObjectName(_fromUtf8("right_grid_layout"))
        
       """
        font = QtGui.QFont()
        font.setBold(True)
        font.setUnderline(False)
        font.setWeight(75)
       
        MainWindow.setCentralWidget(self.centralwidget)
        """
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1080, 27))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        """

        # add all the correct labels
        self.retranslateUi(MainWindow)
        
        # connect the LCD to the Servo speed dial
        QtCore.QObject.connect(self.servo_dial, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), self.servo_display.display)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
        #button clicked controls for the various buttons and checkboxes on the GUI
        # Select All / None button
        self.skut_toggle.clicked.connect(self.skut_toggler)
        
        # Send update button
        self.skut_update.clicked.connect(self.skutter_update)
                        
        # hue slider
        self.hue_slider.sliderMoved.connect(self.HSVtoHEXupload) 
        self.hue_slider.valueChanged.connect(self.HSVtoHEXupload) 
        # brightness slider
        self.bright_slider.sliderMoved.connect(self.HSVtoHEXupload) 
        self.bright_slider.valueChanged.connect(self.HSVtoHEXupload)
               
    def skut_toggler(self):
        self.skut1.setChecked(True)
        global checkbox_status
        if checkbox_status == False:
            self.skut1.setChecked(True)
            self.skut2.setChecked(True)
            self.skut3.setChecked(True)
            self.skut4.setChecked(True)
            self.skut5.setChecked(True)
            self.skut6.setChecked(True)
            self.skut7.setChecked(True)
            self.skut8.setChecked(True)
            self.skut9.setChecked(True)
            checkbox_status = True
        else:
            self.skut1.setChecked(False)
            self.skut2.setChecked(False)
            self.skut3.setChecked(False)
            self.skut4.setChecked(False)
            self.skut5.setChecked(False)
            self.skut6.setChecked(False)
            self.skut7.setChecked(False)
            self.skut8.setChecked(False)
            self.skut9.setChecked(False)
            checkbox_status = False
            
    def skutter_update(self):
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/skutter_18:FE:34:F4:D6:F4", self.skut1.isChecked())
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/skutter_18:FE:34:F4:D4:79", self.skut2.isChecked())
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/skutter_5C:CF:7F:0E:2C:EA", self.skut3.isChecked())
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/skutter_5C:CF:7F:01:59:76", self.skut4.isChecked())
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/skutter_18:FE:34:F4:D3:BD", self.skut5.isChecked())
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/skutter_5C:CF:7F:01:59:5B", self.skut6.isChecked())
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/skutter_5C:CF:7F:0E:35:2D", self.skut7.isChecked())
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/skutter_18:FE:34:FD:92:D1", self.skut8.isChecked())
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/skutter_5C:CF:7F:0E:31:16", self.skut9.isChecked())
        self.settings_update()
        
    def settings_update(self):
        # publish the servo speed
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/speed", self.servo_dial.value())
        
        # publish the time for the colour changed
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
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/colour", hex_colour)
        
        # publish the radio value for the fade or wheel
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        if self.trans_wheel.isChecked() == True:
            mqttc.publish("wishing/transition", "wheel")
        else:
            mqttc.publish("wishing/transition", "fade")
            
        # publish the radio value for the direction
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        if self.clockwise.isChecked() == True:
            mqttc.publish("wishing/direction", "clockwise")
        else:
            mqttc.publish("wishing/direction", "anticlockwise")
        
    def HSVtoHEXupload(self):
        s = 1
        v = self.bright_slider.value() /100.0
        h = self.hue_slider.value() / 100.0
        # convert the HSV to RGB
        rgb_colours = colorsys.hsv_to_rgb(h,s,v)
        
        #convert the RGB to HEX
        hex_colour = colors.rgb2hex((rgb_colours[0], rgb_colours[1], rgb_colours[2]))

        # and update the colour frame on the GUI
        self.colour_display.setStyleSheet("QFrame { background-color: %s}" % hex_colour)
    
    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.servo_control_label.setText(_translate("MainWindow", "Servo Control", None))
        self.colour_control_label.setText(_translate("MainWindow", "Colour Control", None))
        self.skut3.setText(_translate("MainWindow", "skutter 3", None))
        self.brightness_label.setText(_translate("MainWindow", "Brightness", None))
        self.hue_label.setText(_translate("MainWindow", "Hue", None))
        self.skut4.setText(_translate("MainWindow", "skutter 4", None))
        self.skut9.setText(_translate("MainWindow", "skutter 9", None))
        self.skut1.setText(_translate("MainWindow", "skutter 1", None))
        self.trans_wheel.setText(_translate("MainWindow", "Wheel", None))
        self.tran_fade.setText(_translate("MainWindow", "Fade", None))
        self.skut6.setText(_translate("MainWindow", "skutter 6", None))
        self.skut2.setText(_translate("MainWindow", "skutter 2", None))
        self.skut5.setText(_translate("MainWindow", "skutter 5", None))
        self.skut7.setText(_translate("MainWindow", "skutter 7", None))
        self.skut8.setText(_translate("MainWindow", "skutter 8", None))
        self.skutter_control_label.setText(_translate("MainWindow", "Skutter Control", None))
        self.trans_time_label.setText(_translate("MainWindow", "Time (seconds)", None))
        self.skut_update.setText(_translate("MainWindow", "Send Update", None))
        self.skut_toggle.setText(_translate("MainWindow", "All/None", None))
        self.clockwise.setText(_translate("MainWindow", "Clockwise", None))
        self.anticlockwise.setText(_translate("MainWindow", "Anticlock", None))

if __name__ == "__main__":
    import sys

    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    
    sys.exit(app.exec_())

