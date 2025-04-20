import sys
from qt import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QCompleter  


from rolesOpste import rolesOpsteDict
from rolesHR import rolesHRDict
from rolesProjekti import rolesProjektiDict

from updateDropDown import update_dropdown
from dropDownFunctions import clear_all_dropdowns, get_data
from upis import upisi

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
        self.dropDownProjekti2.setEnabled(False)
        self.dropDownProjekti3.setEnabled(False)

        # Populate 1st dropdown for each category  
        self.dropDownOpste1.addItems(rolesOpsteDict.keys())
        self.dropDownHR1.addItems(rolesHRDict.keys())
        self.dropDownProjekti1.addItems(rolesProjektiDict.keys())

        type = None
        # Connect signals to update dropdowns dynamically, passing current items on the window
        self.dropDownOpste1.currentIndexChanged.connect(lambda: update_dropdown(self, 1, 2, rolesOpsteDict, type='o'))
        self.dropDownOpste2.currentIndexChanged.connect(lambda: update_dropdown(self, 2, 3, rolesOpsteDict, type='o'))
        self.dropDownOpste3.currentIndexChanged.connect(lambda: update_dropdown(self, 3, 4, rolesOpsteDict, type='o'))
        self.dropDownHR1.currentIndexChanged.connect(lambda: update_dropdown(self, 1, 2, rolesHRDict, type='h'))
        self.dropDownHR2.currentIndexChanged.connect(lambda: update_dropdown(self, 2, 3, rolesHRDict, type='h'))
        self.dropDownProjekti1.currentIndexChanged.connect(lambda: update_dropdown(self, 1, 2, rolesProjektiDict, type='p'))
        self.dropDownProjekti2.currentIndexChanged.connect(lambda: update_dropdown(self, 2, 3, rolesProjektiDict, type='p'))

        # Push botton listening
        self.upisiButtonLeft.clicked.connect(self.onUpisiButtonLeftClicked)

    def onUpisiButtonLeftClicked(self):
        opsteData = get_data(window=window, type='o')
        HRData = get_data(window=window, type='h')
        projektiData = get_data(window=window, type='p')
        batch = [opsteData, HRData, projektiData]
        upisi(batch)
    def go_to_spc(self):
        self.stackedWidget.setCurrentIndex(1)

    def go_to_mainMenu(self):
        clear_all_dropdowns(window)
        self.dropDownOpste1.addItems(rolesOpsteDict.keys())
        self.dropDownHR1.addItems(rolesHRDict.keys())
        self.dropDownProjekti1.addItems(rolesProjektiDict.keys())
        self.stackedWidget.setCurrentIndex(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())