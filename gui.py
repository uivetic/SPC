import sys
from qt import Ui_MainWindow
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QCompleter, QMessageBox, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QComboBox, QPushButton, QScrollArea, QDialog
)

from rolesOpste import rolesOpsteDict
from rolesHR import rolesHRDict
from rolesProjekti import rolesProjektiDict

from updateDropDown import update_dropdown
from dropDownFunctions import clear_all_dropdowns, get_data, get_points_for_activity
from upis import upisi

"""Sheet connection"""
from sheetConnection import names_list


class NameDropdownPopup(QDialog):
    def __init__(self, names, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Name Dropdowns")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        self.combo_boxes = []

        selected_type = self.parent().get_selected_type()
        points = []

        if selected_type:
            points = get_points_for_activity(window=self.parent(), type=selected_type)

        for name in names:
            row = QHBoxLayout()
            label = QLabel(name)
            combo = QComboBox()
            #combo.addItem("")
            combo.addItems(points)
            row.addWidget(label)
            row.addWidget(combo)
            scroll_layout.addLayout(row)
            self.combo_boxes.append(combo)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        button_row = QHBoxLayout()
        button_row.addStretch()
        upisi_button = QPushButton("Upiši")
        upisi_button.clicked.connect(self.submit)
        button_row.addWidget(upisi_button)
        layout.addLayout(button_row)

        self.setLayout(layout)

    def submit(self):
        values = [combo.currentText() for combo in self.combo_boxes]
        if all(value.currentText != "" for value in self.combo_boxes):
            values = [value.currentText() for value in self.combo_boxes]
            self.accept()
            return values
        else:
            QMessageBox.warning("Upozorenje", "Niste upisali poene za sve osobe!")
            


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

        # Deleting last added name or selected name
        self.removeNameButton.clicked.connect(self.onRemoveNameClicked)

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
        return (window.dropDownHR3.isEnabled() and window.dropDownHR3.selected().currentText()) or (window.dropDownOpste4.isEnabled() and window.dropDownOpste4.currentText()) or (window.dropDownProjekti3.isEnabled() and window.dropDownProjekti3.currentText())

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
            print(batch)
            points = [b[-1] for b in batch if b]
            pairs = [(name, point) for name in names for point in points]
            upisi(batch, pairs)
            QMessageBox.information(self, "Uspeh", "Bodovi upisani!")
            window.allPersonsRight.clear()
        else:
            if not self.allPersonsRight.toPlainText().strip() == '': 
                popup = NameDropdownPopup(names, self)
                popup.exec_()
                points = popup.submit()
                pairs = list(zip(names, points))
                print(pairs)
                upisi(batch, pairs)
                QMessageBox.information(self, "Uspeh", "Bodovi upisani!")
                window.allPersonsRight.clear()
            else:
                QMessageBox.warning(self, "Greška", "Dodaj ime za upis!")
        clear_all_dropdowns(self)
        self.dropDownOpste1.addItems(rolesOpsteDict.keys())
        self.dropDownHR1.addItems(rolesHRDict.keys())
        self.dropDownProjekti1.addItems(rolesProjektiDict.keys())
    
    def get_selected_type(self):
        if self.dropDownOpste1.isEnabled():
            return 'o'
        if self.dropDownHR1.isEnabled():
            return 'h'
        if self.dropDownProjekti1.isEnabled():
            return 'p'
        return None

    def onAddButtonRIghtClicked(self):
        names = self.return_names()
        name = window.namesRightLineEdit.text()
        if name in names_list and name not in names:
            self.allPersonsRight.appendPlainText(name)
            self.namesRightLineEdit.clear()
        else:
            QMessageBox.warning(self, "Upozorenje", "Ime ne postoji u bazi ili je već dodato")
            self.namesRightLineEdit.clear()
    
    def onRemoveNameClicked(self):
        cursor = self.allPersonsRight.textCursor()
        cursor.select(cursor.LineUnderCursor)
        selected_text = cursor.selectedText().strip()

        names = self.return_names()

        if selected_text:
            # Remove selected name
            names = [name for name in names if name.strip() != selected_text]
        elif names:
            # No selection: remove last
            names.pop()

        self.allPersonsRight.setPlainText('\n'.join(names))

    def go_to_spc(self):
        self.stackedWidget.setCurrentIndex(1)

    def go_to_mainMenu(self):
        clear_all_dropdowns(window)
        self.namesRightLineEdit.clear()
        self.dropDownOpste1.addItems(rolesOpsteDict.keys())
        self.dropDownHR1.addItems(rolesHRDict.keys())
        self.dropDownProjekti1.addItems(rolesProjektiDict.keys())
        self.enable_all_first_dropdowns()
        self.stackedWidget.setCurrentIndex(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
