import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QCompleter
from PyQt5.QtCore import QStringListModel
from qt import Ui_MainWindow  
import gspread 
from google.oauth2.service_account import Credentials
import unicodedata
import sys
import os
from rolesOpste import rolesOpste, rolesOpsteDict, kvartaliGodisnji
import rolesHR
import rolesProjekti
from PyQt5.QtWidgets import QComboBox


# resava qt.qpa.wayland: Wayland does not support QWindow::requestActivate()
if sys.platform.startswith("linux"):
    os.environ["QT_QPA_PLATFORM"] = "xcb"


#Normalizacija imena tako da uroš -> uros
def normalize_name(input_str):

    normalized_str = unicodedata.normalize('NFD', input_str)
    return ''.join([c for c in normalized_str if unicodedata.category(c) != 'Mn'])

#POVEZIVANJE SA SHEETOM
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("../credentials.json", scopes=scopes)
client = gspread.authorize(creds)

# Otvori tabelu
sheet_id = "1UMMIeubY1-v5AKrXXiCf9TOQjBgNjOfzeqvelGMEPbA"
workbook = client.open_by_key(sheet_id)

worksheet_list = map(lambda x: x.title, workbook.worksheets())
#print(list(worksheet_list))

sheet = workbook.worksheet("ZBIR")
all_values = sheet.get_all_values()

names_list = [row[1] for row in all_values[6:] if isinstance(row[1], str)]

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

        self.dropDownOpste1.addItem("")
        self.dropDownOpste2.addItem("")  # Initially empty
        self.dropDownOpste3.addItem("")  # Initially empty
        self.dropDownOpste4.addItem("")  # Initially empty
        self.dropDownOpste1.addItems(rolesOpste)

        # Connect signals to update dropdowns dynamically
        self.dropDownOpste1.currentIndexChanged.connect(lambda: self.update_dropdown(1, 2, rolesOpsteDict))
        self.dropDownOpste2.currentIndexChanged.connect(lambda: self.update_dropdown(2, 3, rolesOpsteDict))
        self.dropDownOpste3.currentIndexChanged.connect(lambda: self.update_dropdown(3, 4, rolesOpsteDict))


    def update_dropdown(self, current_index, next_index, data_dict):
        """Updates the next dropdown based on the selected value of the current dropdown."""
        # Get selected value from current dropdown
        selected_value = self.get_previous_selection(current_index)
        # Get reference to next dropdown
        next_dropdown = getattr(self, f"dropDownOpste{next_index}", None)

        # if not next_dropdown:
        #     print('ovde return')
        #     return  # Exit if dropdown doesn't exist
        if not selected_value:
            self.clear_all_dropdowns_below(current_index)
            return
        next_dropdown.clear()  # Clear previous items

        # Use lambda to get new options based on selected value
        print(current_index, next_index)
        if next_index == 3:
            # print(rolesOpsteDict[self.dropDownOpste1.currentText()])
            # options = self.get_roles(rolesOpsteDict[self.dropDownOpste1.currentText()].keys())
            options = self.numbers_list_string_list(kvartaliGodisnji)
            print(options)
        elif next_index == 4:
            options = self.numbers_list_string_list(rolesOpsteDict[self.dropDownOpste1.currentText()][self.dropDownOpste2.currentText()])
            #options = self.numbers_list_string_list(options)
            print(options)
        else:
            options = (lambda value: list(data_dict.get(value, {}).keys()))(selected_value)
        if options:
            next_dropdown.addItem("")
            next_dropdown.addItems(options)
            next_dropdown.setEnabled(True)
        else:
            next_dropdown.setEnabled(False)
            next_dropdown.addItem("")  # Add empty item to prevent issues

    # Reset all subsequent dropdowns
    def clear_all_dropdowns_below(self, next_index):
        for i in range(next_index + 1, 5):
            dropdown = getattr(self, f"dropDownOpste{i}", None)
            if dropdown:
                dropdown.clear()
                dropdown.setEnabled(False)

    def numbers_list_string_list(self, numbers_list):
        return [str(number) for number in numbers_list]
    def get_roles(self, map):
        roles = []
        for key in map:
            roles.append(key)
        return roles
    def get_previous_selection(self, num):
        dropdown = getattr(self, f"dropDownOpste{num}", None)
        return dropdown.currentText() if dropdown else None
    def get_combo_items(comboBox):
        return [comboBox.itemText(i) for i in range(comboBox.count())]
    def go_to_spc(self):
        self.stackedWidget.setCurrentIndex(1)
    def go_to_mainMenu(self):
         self.stackedWidget.setCurrentIndex(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())