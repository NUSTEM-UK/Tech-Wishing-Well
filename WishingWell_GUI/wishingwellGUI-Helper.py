def skutter_setup():

# PyQT4 code for the Skutter Checkboxes
        # Step 1 - define the QCheckbox as part of the self.gridLayoutWidget
        # Step 2 - name the QCheckbox
        # Step 3 - place the checkbox in the correct row and column in the left_grid_layout
        self.skut1 = QtGui.QCheckBox(self.gridLayoutWidget)
        self.skut1.setObjectName(_fromUtf8("skut1"))
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