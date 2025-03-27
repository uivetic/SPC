import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QCompleter
from PyQt5.QtCore import QStringListModel
from qt import Ui_MainWindow  
import gspread 
from google.oauth2.service_account import Credentials
import unicodedata
import sys
import os
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
        # completer za imena
        completer = QCompleter(names_list)
        completer.setCaseSensitivity(False)


        # completer za imena
        self.nameLineEditLeft.setCompleter(completer)

        # dugmad za ulazak i izlazak iz upisivanja
        self.spcPushButton.clicked.connect(self.go_to_spc)
        # self.backButtonLeft.clicked.connect(self.go_to_mainMenu)
        
        # opste combo-boxevi

        print(type(self.dropDownOpste1))
        print(type(self.dropDownOpste2))
        print(type(self.dropDownOpste3))
        print(type(self.dropDownOpste4))

        self.dropDownOpste1.addItems(["", "Option 1", "Option 2", "Option 3"])
        self.dropDownOpste2.addItems(["", "A", "B", "C"])
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

    

    def get_combo_items(comboBox):
        return [comboBox.itemText(i) for i in range(comboBox.count())]
    def go_to_spc(self):
        self.stackedWidget.setCurrentIndex(1)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())