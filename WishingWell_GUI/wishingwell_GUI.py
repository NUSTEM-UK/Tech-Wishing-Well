##############################################################################
# This code outputs data from the GUI to the following MQTT topics on        #
# 'localhost', port '1883'                                                   #
#                                                                            #
#   Topic/Subtopic                      Values                               #
#   wishing/scutter_MAC_ADDRESS         bool True / False                    #
#   Wishing/speed                       int 0 - 100                          #
#   wishing/colour                      hex colour code                      #
#   wishing/time                        int >= 1                             #
#   wishing/transition                  wheel / fade                         #
#   wishing/direction                   0 / 1                                #
#                                                                            #
##############################################################################

# Install: needs:
# sudo pip install paho-mqtt
# sudo apt install python-matplotlib
# Requires a *local* mqtt broker, for example via:
# sudo apt install mosquitto

from PyQt4 import QtCore, QtGui
import paho.mqtt.client as mqtt

# these modules allow us to convert a HSV colour value to a HEX code (via RGB)
import matplotlib.colors as colors
import colorsys

checkbox_status = True

class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.resize(540, 500)
        MainWindow.setWindowTitle("Technology Wishing Well HUD")
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.gridLayoutWidget = QtGui.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(40, 20, 462, 432))

        # define the font for the headings
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)

        # setup the grid that all the objects will be placed within
        self.left_grid_layout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.left_grid_layout.setMargin(0)

        # this group box confine the wheel/fade radio checkboxes
        self.groupBox = QtGui.QGroupBox(self.centralwidget)
        # give the group an invisible background (default is a shade of grey
        self.groupBox.setFlat(True)
        # put the group into the correct position in the grid layout
        self.left_grid_layout.addWidget(self.groupBox, 7, 2, 1, 1)
        # this group box confines the wheel/fade radio checkboxes
        self.groupBox2 = QtGui.QGroupBox(self.centralwidget)
        self.groupBox2.setFlat(True)
        self.left_grid_layout.addWidget(self.groupBox2, 8, 0, 1, 1)

        # Skutter control label
        self.skutter_control_label = QtGui.QLabel("Skutter control", self.gridLayoutWidget)
        self.skutter_control_label.setFont(font)
        self.left_grid_layout.addWidget(self.skutter_control_label, 0, 0, 1, 1)

        # PyQT4 code for the Skutter Checkboxes
        # Step 1 - define the QCheckbox as part of the self.gridLayoutWidget
        # Step 2 - place the checkbox in the correct row and column in the left_grid_layout
        self.skut1 = QtGui.QCheckBox("skutter 1", self.gridLayoutWidget)
        self.left_grid_layout.addWidget(self.skut1, 1, 0, 1, 1)

        self.skut2 = QtGui.QCheckBox("skutter 2", self.gridLayoutWidget)
        self.left_grid_layout.addWidget(self.skut2, 1, 1, 1, 1)

        self.skut3 = QtGui.QCheckBox("skutter 3", self.gridLayoutWidget)
        self.left_grid_layout.addWidget(self.skut3, 1, 2, 1, 1)

        self.skut4 = QtGui.QCheckBox("skutter 4", self.gridLayoutWidget)
        self.left_grid_layout.addWidget(self.skut4, 2, 0, 1, 1)

        self.skut5 = QtGui.QCheckBox("skutter 5", self.gridLayoutWidget)
        self.left_grid_layout.addWidget(self.skut5, 2, 1, 1, 1)

        self.skut6 = QtGui.QCheckBox("skutter 6", self.gridLayoutWidget)
        self.left_grid_layout.addWidget(self.skut6, 2, 2, 1, 1)

        self.skut7 = QtGui.QCheckBox("skutter 7", self.gridLayoutWidget)
        self.left_grid_layout.addWidget(self.skut7, 3, 0, 1, 1)

        self.skut8 = QtGui.QCheckBox("skutter 8", self.gridLayoutWidget)
        self.left_grid_layout.addWidget(self.skut8, 3, 1, 1, 1)

        self.skut9 = QtGui.QCheckBox("skutter 9", self.gridLayoutWidget)
        self.left_grid_layout.addWidget(self.skut9, 3, 2, 1, 1)


        # Add the label for the servo control
        self.servo_control_label = QtGui.QLabel("Servo control", self.gridLayoutWidget)
        self.servo_control_label.setFont(font)
        self.left_grid_layout.addWidget(self.servo_control_label, 6, 0, 1, 1)

        # add the bold label for the colour control
        self.colour_control_label = QtGui.QLabel("Colour control", self.gridLayoutWidget)
        self.colour_control_label.setFont(font)
        self.left_grid_layout.addWidget(self.colour_control_label, 6, 1, 1, 1)

        # create a vertical layout to go within the grid to hold the hue and brightness sliders
        self.vertical_layout_colour = QtGui.QVBoxLayout()

        # create a label for the brightness slider
        self.brightness_label = QtGui.QLabel("Brightness", self.gridLayoutWidget)
        self.vertical_layout_colour.addWidget(self.brightness_label)

        #create the brightness slider and add to the vertical layout
        self.bright_slider = QtGui.QSlider(self.gridLayoutWidget)
        self.bright_slider.setOrientation(QtCore.Qt.Horizontal)
        self.vertical_layout_colour.addWidget(self.bright_slider)

        # create a label for the hue slider
        self.hue_label = QtGui.QLabel("Hue", self.gridLayoutWidget)
        self.vertical_layout_colour.addWidget(self.hue_label)

        # create the hue slider
        self.hue_slider = QtGui.QSlider(self.gridLayoutWidget)
        self.hue_slider.setOrientation(QtCore.Qt.Horizontal)
        self.vertical_layout_colour.addWidget(self.hue_slider)

        # create a frame which will display the current colour choice
        self.colour_display = QtGui.QFrame(self.gridLayoutWidget)
        self.left_grid_layout.addWidget(self.colour_display, 8, 1, 1, 1)
        self.colour_display.setFixedSize(100,30)
        self.colour_display.setFrameShape(QtGui.QFrame.WinPanel)
        self.colour_display.setFrameShadow(QtGui.QFrame.Raised)

        self.left_grid_layout.addLayout(self.vertical_layout_colour, 7, 1, 1, 1)

        # create a vertical layout box to house the trans and fade radio buttons
        # add this to the group1 box to ensure toggle-ability
        self.vertical_layout_wheel = QtGui.QVBoxLayout(self.groupBox)

        # add the trans radio button to the vertical layout
        self.trans_wheel = QtGui.QRadioButton("Wheel", self.gridLayoutWidget)
        self.vertical_layout_wheel.addWidget(self.trans_wheel)

        # add the fade radio button to the vertical layout
        self.tran_fade = QtGui.QRadioButton("Fade", self.gridLayoutWidget)
        self.vertical_layout_wheel.addWidget(self.tran_fade)
        self.trans_wheel.setChecked(True)

        # add the clockwise and anticlockwise radios to vertical and group 2
        self.vertical_layout_direction = QtGui.QVBoxLayout(self.groupBox2)
        self.clockwise = QtGui.QRadioButton("Forward", self.gridLayoutWidget)
        self.vertical_layout_direction.addWidget(self.clockwise)
        self.anticlockwise = QtGui.QRadioButton("Reverse", self.gridLayoutWidget)
        self.vertical_layout_direction.addWidget(self.anticlockwise)
        self.clockwise.setChecked(True)

        # vertical layout for the servo control
        self.vertical_layout_servo = QtGui.QVBoxLayout()

        # the servo dial and LCD setup
        self.servo_dial = QtGui.QDial(self.gridLayoutWidget)
        self.servo_dial.setNotchesVisible(True)
        self.vertical_layout_servo.addWidget(self.servo_dial)
        self.servo_display = QtGui.QLCDNumber(self.gridLayoutWidget)
        self.vertical_layout_servo.addWidget(self.servo_display)
        self.left_grid_layout.addLayout(self.vertical_layout_servo, 7, 0, 1, 1)

        # vertical layout for transition time
        self.vertical_layout_time = QtGui.QVBoxLayout()

        # add the label for the transition time QSpinBox
        self.trans_time_label = QtGui.QLabel("Time (s)", self.gridLayoutWidget)
        self.vertical_layout_time.addWidget(self.trans_time_label)

        # add the transition time QSpinBox to the vertical layout within the grid
        self.trans_time = QtGui.QSpinBox(self.gridLayoutWidget)
        self.vertical_layout_time.addWidget(self.trans_time)
        self.left_grid_layout.addLayout(self.vertical_layout_time, 7, 3, 1, 1)
        self.trans_time.setMinimum(1)
        # add the skutter update button
        self.skut_update = QtGui.QPushButton("Send Update", self.gridLayoutWidget)
        self.left_grid_layout.addWidget(self.skut_update, 8, 3, 1, 1)

        # add the skutter on/off toggle button
        self.skut_toggle = QtGui.QPushButton("All / None", self.gridLayoutWidget)
        self.skut_toggle.setFixedSize(80, 30)
        self.left_grid_layout.addWidget(self.skut_toggle, 4, 3, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        # connect the LCD to the Servo speed dial
        QtCore.QObject.connect(self.servo_dial, QtCore.SIGNAL("valueChanged(int)"), self.servo_display.display)
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
        mqttc.publish("wishing/skutter_18:FE:34:F4:D6:F4", bool(self.skut1.isChecked()))
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/skutter_18:FE:34:F4:D4:79", bool(self.skut2.isChecked()))
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/skutter_5C:CF:7F:0E:2C:EA", bool(self.skut3.isChecked()))
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/skutter_5C:CF:7F:01:59:76", bool(self.skut4.isChecked()))
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/skutter_18:FE:34:F4:D3:BD", bool(self.skut5.isChecked()))
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/skutter_5C:CF:7F:01:59:5B", bool(self.skut6.isChecked()))
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/skutter_5C:CF:7F:0E:35:2D", bool(self.skut7.isChecked()))
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/skutter_18:FE:34:FD:92:D1", bool(self.skut8.isChecked()))
        mqttc = mqtt.Client("python_pub")
        mqttc.connect('localhost', 1883)
        mqttc.publish("wishing/skutter_5C:CF:7F:0E:31:16", bool(self.skut9.isChecked()))
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

        self.HSVtoHEXupload()

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
            mqttc.publish("wishing/direction", 1)
        else:
            mqttc.publish("wishing/direction", 0)

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

if __name__ == "__main__":
    import sys

    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()

    sys.exit(app.exec_())
