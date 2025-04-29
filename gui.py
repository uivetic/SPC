import sys
from qt import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QCompleter, QMessageBox

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
        self.allPersonsRight.setReadOnly(True)
        
        # Name completer
        completer = QCompleter(names_list)
        completer.setCaseSensitivity(False)
        self.nameLineEditLeft.setCompleter(completer)
        self.namesRightLineEdit.setCompleter(completer)

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
        # Connect signals to update dropdowns dynamically
        self.dropDownOpste1.currentIndexChanged.connect(lambda: update_dropdown(self, 1, 2, rolesOpsteDict, type='o'))
        self.dropDownOpste2.currentIndexChanged.connect(lambda: update_dropdown(self, 2, 3, rolesOpsteDict, type='o'))
        self.dropDownOpste3.currentIndexChanged.connect(lambda: update_dropdown(self, 3, 4, rolesOpsteDict, type='o'))
        self.dropDownHR1.currentIndexChanged.connect(lambda: update_dropdown(self, 1, 2, rolesHRDict, type='h'))
        self.dropDownHR2.currentIndexChanged.connect(lambda: update_dropdown(self, 2, 3, rolesHRDict, type='h'))
        self.dropDownProjekti1.currentIndexChanged.connect(lambda: update_dropdown(self, 1, 2, rolesProjektiDict, type='p'))
        self.dropDownProjekti2.currentIndexChanged.connect(lambda: update_dropdown(self, 2, 3, rolesProjektiDict, type='p'))

        # Connect signals to enforce single selection
        self.dropDownOpste1.currentIndexChanged.connect(lambda: self.disable_other_first_dropdowns('o'))
        self.dropDownHR1.currentIndexChanged.connect(lambda: self.disable_other_first_dropdowns('h'))
        self.dropDownProjekti1.currentIndexChanged.connect(lambda: self.disable_other_first_dropdowns('p'))

        # Push button listeners
        self.upisiButtonLeft.clicked.connect(self.onUpisiButtonLeftClicked)
        self.addButtonRight.clicked.connect(self.onAddButtonRIghtClicked)

    def disable_other_first_dropdowns(self, changed):
        dropdowns = {
            "o": self.dropDownOpste1,
            "h": self.dropDownHR1,
            "p": self.dropDownProjekti1
        }

        # If a selection is made (not the empty/default item), disable the others
        if dropdowns[changed].currentIndex() != 0:
            for key, dropdown in dropdowns.items():
                if key != changed:
                    dropdown.setEnabled(False)
        else:
            # If user resets the selection to the first item, re-enable all
            self.enable_all_first_dropdowns()

    def enable_all_first_dropdowns(self):
        self.dropDownOpste1.setEnabled(True)
        self.dropDownHR1.setEnabled(True)
        self.dropDownProjekti1.setEnabled(True)

    def proveri(self, batch, name):
        return name and any(len(d) > 2 for d in batch)
    def upisani_poeni(self):
        return window.dropDownHR3 or window.dropDownOpste4 or window.dropDownProjekti3
    def return_names(self):
        addedNames = self.allPersonsRight.toPlainText()
        names = addedNames.split('\n')
        return names     
    def onUpisiButtonLeftClicked(self):
        opsteData = get_data(window=window, type='o')
        HRData = get_data(window=window, type='h')
        projektiData = get_data(window=window, type='p')
        names = self.return_names()
        batch = [opsteData, HRData, projektiData]
        check = self.proveri(batch, names)
        if check and self.upisani_poeni():
            upisi(batch, names)
            QMessageBox.information(self, "Uspeh", "Bodovi upisani!")
            window.allPersonsRight.clear()
        else:
            # TODO
            print("jeej")
            # popup sa imenima i listom bodova
        
    def onAddButtonRIghtClicked(self):
        names = self.return_names()
        name = window.namesRightLineEdit.text()
        if name in names_list and name not in names:
            self.allPersonsRight.appendPlainText(name)
            self.namesRightLineEdit.clear()
        else:
            QMessageBox.warning(self, "Upozorenje", "Ime ne postoji u bazi ili je već dodato")
            self.namesRightLineEdit.clear()

    def go_to_spc(self):
        self.stackedWidget.setCurrentIndex(1)

    def go_to_mainMenu(self):
        clear_all_dropdowns(window)
        self.dropDownOpste1.addItems(rolesOpsteDict.keys())
        self.dropDownHR1.addItems(rolesHRDict.keys())
        self.dropDownProjekti1.addItems(rolesProjektiDict.keys())
        self.enable_all_first_dropdowns()  # Re-enable all first dropdowns
        self.stackedWidget.setCurrentIndex(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())