#Opste combo-boxes
        self.dropDownOpste1.addItems(rolesOpste)
        self.dropDownOpste2.addItems(
            
        )
        self.dropDownOpste3.addItems(["", "X", "Y", "Z"])
        self.dropDownOpste4.addItems(["", "Red", "Blue", "Green"])

        self.dropDownOpste2.setEnabled(False)
        self.dropDownOpste3.setEnabled(False)
        self.dropDownOpste4.setEnabled(False)

        # Connect signals to update next combo box
        self.dropDownOpste1.currentIndexChanged.connect(self.update_dropDownOpste2)
        self.dropDownOpste2.currentIndexChanged.connect(self.update_dropDownOpste3)
        self.dropDownOpste3.currentIndexChanged.connect(self.update_dropDownOpste4)


    def update_dropDownOpste2(self):
        """Enable dropDownOpste2 if dropDownOpste1 has a selection"""
        self.dropDownOpste2.setEnabled(bool(self.dropDownOpste1.currentText()))
        if not self.dropDownOpste1.currentText():  # Reset subsequent selections
            self.dropDownOpste2.setCurrentIndex(0)
            self.dropDownOpste3.setCurrentIndex(0)
            self.dropDownOpste4.setCurrentIndex(0)
            self.dropDownOpste3.setEnabled(False)
            self.dropDownOpste4.setEnabled(False)

    def update_dropDownOpste3(self):
        """Enable dropDownOpste3 if dropDownOpste2 has a selection"""
        self.dropDownOpste3.setEnabled(bool(self.dropDownOpste2.currentText()))
        if not self.dropDownOpste2.currentText():
            self.dropDownOpste3.setCurrentIndex(0)
            self.dropDownOpste4.setCurrentIndex(0)
            self.dropDownOpste4.setEnabled(False)

    def update_dropDownOpste4(self):
        """Enable dropDownOpste4 if dropDownOpste3 has a selection"""
        self.dropDownOpste4.setEnabled(bool(self.dropDownOpste3.currentText()))
        if not self.dropDownOpste3.currentText():
            self.dropDownOpste4.setCurrentIndex(0)