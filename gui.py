import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QCompleter
from PyQt5.QtCore import QStringListModel
from qt import Ui_MainWindow  
import gspread 
from google.oauth2.service_account import Credentials
import unicodedata
import sys
import os


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



        self.lineEdit.setCompleter(completer)
        self.pushButton.clicked.connect(self.go_to_spc)
        self.nazadButton.clicked.connect(self.go_to_mainMenu)
        self.comboBoxProjekat.currentIndexChanged.connect(self.on_project_changed)
        self.comboBoxUloga.currentIndexChanged.connect(self.on_role_changed)
        self.comboBoxUloga.setEnabled(False)
        self.comboBoxBodovi.setEnabled(False)

    def go_to_spc(self):
        self.stackedWidget.setCurrentIndex(1)
    
    def go_to_mainMenu(self):
        self.stackedWidget.setCurrentIndex(0)
    
    def on_project_changed(self, index):
        print("Selected:", self.comboBoxProjekat.itemText(index))
        if len(self.comboBoxProjekat.itemText(index)) > 0:
            self.comboBoxUloga.setEnabled(True)
        else:
            #self.comboBoxUloga.setText("")
            self.comboBoxUloga.setEnabled(False)
            self.comboBoxUloga.setCurrentIndex(0)

    
    def on_role_changed(self, index):
        #items = self.get_combo_items(self.comboBoxUloga)
        if self.comboBoxUloga.itemText(index) == "PR Tim" or self.comboBoxUloga.itemText(index) == "FR Tim":
            self.comboBoxBodovi.clear()
            self.comboBoxBodovi.setEnabled(True)
            self.comboBoxBodovi.insertItem(0)
            self.comboBoxBodovi.insertItem(1)
            self.comboBoxBodovi.insertItem(2)

        if self.comboBoxUloga.itemText(index) == "CT":
            self.comboBoxBodovi.clear()
            self.comboBoxBodovi.setEnabled(True)
            if self.comboBoxProjekat.itemText(index) == "JobFair" or self.comboBoxProjekat.itemText(index) == "Kurs":
                self.comboBoxBodovi.insertItem("4")
                self.comboBoxBodovi.insertItem("8")
                self.comboBoxBodovi.insertItem("12")
                self.comboBoxBodovi.insertItem("16")
                self.comboBoxBodovi.insertItem("20")
                self.comboBoxBodovi.insertItem("24")
            else:
                self.comboBoxBodovi.insertItem("4")
                self.comboBoxBodovi.insertItem("8")
                self.comboBoxBodovi.insertItem("12")

    def get_combo_items(comboBox):
        return [comboBox.itemText(i) for i in range(comboBox.count())]
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())