import sys
from qt import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QCompleter  


from rolesOpste import rolesOpsteDict
from rolesHR import rolesHRDict
import rolesProjekti

from updateOpsteDropDown import update_dropdown

"""Sheet connection"""
from sheetConnection import names_list


class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self) 
        self.stackedWidget.setCurrentIndex(0)
        
        # Name completer
        completer = QCompleter(names_list)
        completer.setCaseSensitivity(False)
        self.nameLineEditLeft.setCompleter(completer)

        # Enter/exit push buttons
        self.spcPushButton.clicked.connect(self.go_to_spc)
        self.backButtonLeft.clicked.connect(self.go_to_mainMenu)
        
        # Disable dropdowns initially
        self.dropDownOpste2.setEnabled(False)
        self.dropDownOpste3.setEnabled(False)
        self.dropDownOpste4.setEnabled(False)
        self.dropDownHR2.setEnabled(False)
        self.dropDownHR3.setEnabled(False)

        # Each dropdown is initially empty
        self.dropDownOpste1.addItem("")
        self.dropDownOpste2.addItem("")
        self.dropDownOpste3.addItem("")
        self.dropDownOpste4.addItem("")
        self.dropDownHR1.addItem("")
        self.dropDownHR2.addItem("")
        self.dropDownHR3.addItem("")

        #Populate 1st dropdown for each category  
        self.dropDownOpste1.addItems(rolesOpsteDict.keys())
        self.dropDownHR1.addItems(rolesHRDict.keys())

        # Connect signals to update dropdowns dynamically, passing current items on the window
        self.dropDownOpste1.currentIndexChanged.connect(lambda: update_dropdown(self, 1, 2, rolesOpsteDict, 'o'))
        self.dropDownOpste2.currentIndexChanged.connect(lambda: update_dropdown(self, 2, 3, rolesOpsteDict, 'o'))
        self.dropDownOpste3.currentIndexChanged.connect(lambda: update_dropdown(self, 3, 4, rolesOpsteDict, 'o'))
        self.dropDownHR1.currentIndexChanged.connect(lambda: update_dropdown(self, 1, 2, rolesHRDict, 'h'))
        self.dropDownHR2.currentIndexChanged.connect(lambda: update_dropdown(self, 2, 3, rolesHRDict, 'h'))

    def go_to_spc(self):
        self.stackedWidget.setCurrentIndex(1)
    def go_to_mainMenu(self):
         self.stackedWidget.setCurrentIndex(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())