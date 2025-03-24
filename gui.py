import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QCompleter
from PyQt5.QtCore import QStringListModel
from qt import Ui_MainWindow  
import gspread 
from google.oauth2.service_account import Credentials
import unicodedata


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

# cell = sheet.find("Uroš Ivetić")
# print(cell.row, cell.col)

class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self) 
        self.stackedWidget.setCurrentIndex(0)
        # completer za imena
        completer = QCompleter(names_list)
        completer.setCaseSensitivity(False)
        completer.filterMode  

        self.lineEdit.setCompleter(completer)

        self.pushButton.clicked.connect(self.go_to_page2)
        self.nazadButton.clicked.connect(self.go_to_mainMenu)

    def go_to_page2(self):
        
        self.stackedWidget.setCurrentIndex(1)
    
    def go_to_mainMenu(self):
        self.stackedWidget.setCurrentIndex(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())