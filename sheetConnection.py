import os
import sys
import gspread 
import unicodedata
from google.oauth2.service_account import Credentials
from PyQt5.QtCore import QObject, pyqtSignal

# resava qt.qpa.wayland: Wayland does not support QWindow::requestActivate()
if sys.platform.startswith("linux"):
    os.environ["QT_QPA_PLATFORM"] = "xcb"


#Normalize name comparison, uroš -> uros
def normalize_name(input_str):
    if not isinstance(input_str, str):
        return ""
    normalized_str = unicodedata.normalize('NFD', input_str)
    cleaned_str = ''.join([c for c in normalized_str if unicodedata.category(c) != 'Mn'])
    return cleaned_str.lower()

# Google cloud API
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
sheet_id = "17yR3BJzslf4HLMGTDc0OvzRaY3t7VAZ1-CGx5GxQM_Q"


class LazySheetConnection(QObject):
    """Lazy loading klasa za Google Sheets konekciju"""
    names_loaded = pyqtSignal(list, list, list)  # names_list, original_names_list, normalized_names_list
    connection_error = pyqtSignal(str)
    
    def __init__(self, credentials_path="../credentials.json"):
        super().__init__()
        self.credentials_path = credentials_path
        self._workbook = None
        self._client = None
        self._names_list = []
        self._original_names_list = []
        self._normalized_names_list = []
        self._initialized = False
    
    def initialize_sync(self):
        """Brza sinhrona inicijalizacija samo klijenta (ne učitava podatke)"""
        try:
            creds = Credentials.from_service_account_file(self.credentials_path, scopes=scopes)
            self._client = gspread.authorize(creds)
            self._workbook = self._client.open_by_key(sheet_id)
            return True
        except Exception as e:
            print(f"Greška pri inicijalizaciji: {e}")
            return False
    
    def load_names_async(self):
        """Asinhrono učitava names_list (poziva se iz worker thread-a)"""
        try:
            if not self._workbook:
                if not self.initialize_sync():
                    self.connection_error.emit("Neuspešna inicijalizacija konekcije")
                    return
            
            sheet = self._workbook.worksheet("ZBIR")
            all_values = sheet.get_all_values()
            
            # Extracting all names in ZBIR sub-sheet
            names = [row[1] for row in all_values[6:] if isinstance(row[1], str)]
            original_names = [row[1] for row in all_values[6:] if isinstance(row[1], str)]
            normalized_names = [normalize_name(name) for name in original_names]
            
            self._names_list = names
            self._original_names_list = original_names
            self._normalized_names_list = normalized_names
            self._initialized = True
            
            self.names_loaded.emit(names, original_names, normalized_names)
        except Exception as e:
            self.connection_error.emit(f"Greška pri učitavanju imena: {str(e)}")
    
    @property
    def workbook(self):
        """Dobija workbook (lazy initialization)"""
        if not self._workbook:
            self.initialize_sync()
        return self._workbook
    
    @property
    def names_list(self):
        """Dobija names_list (može biti prazan ako još nije učitan)"""
        return self._names_list
    
    @property
    def original_names_list(self):
        """Dobija original_names_list"""
        return self._original_names_list
    
    @property
    def normalized_names_list(self):
        """Dobija normalized_names_list"""
        return self._normalized_names_list
    
    @property
    def is_initialized(self):
        """Proverava da li su podaci učitani"""
        return self._initialized
    
    def get_worksheet_list(self):
        """Dobija listu worksheet-a"""
        if not self._workbook:
            return []
        return [ws.title for ws in self._workbook.worksheets()]


# Kreiraj globalnu instancu za backward compatibility
_lazy_connection = LazySheetConnection()

# Inicijalizuj samo klijent (brzo)
_lazy_connection.initialize_sync()

# Backward compatibility - eksportuj workbook direktno
workbook = _lazy_connection.workbook

# Backward compatibility - eksportuj worksheet_list
worksheet_list = _lazy_connection.get_worksheet_list()

# Backward compatibility - eksportuj prazne liste (biće popunjene asinhrono)
names_list = []
original_names_list = []
normalized_names_list = []
