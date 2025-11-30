from PyQt5.QtCore import QObject, pyqtSignal, QMutex
import gspread
from gspread.exceptions import WorksheetNotFound, APIError
from google.oauth2.service_account import Credentials
from sheetConnection import normalize_name
import re
from gspread.utils import rowcol_to_a1


class SheetConnectionWorker(QObject):
    """Worker za inicijalizaciju Google Sheets konekcije u pozadini"""
    finished = pyqtSignal(object)  # workbook
    error = pyqtSignal(str)
    
    def __init__(self, credentials_path, sheet_id, scopes):
        super().__init__()
        self.credentials_path = credentials_path
        self.sheet_id = sheet_id
        self.scopes = scopes
    
    def run(self):
        try:
            creds = Credentials.from_service_account_file(
                self.credentials_path, 
                scopes=self.scopes
            )
            client = gspread.authorize(creds)
            workbook = client.open_by_key(self.sheet_id)
            self.finished.emit(workbook)
        except Exception as e:
            self.error.emit(f"Greška pri povezivanju sa Google Sheets: {str(e)}")


class SheetDataLoaderWorker(QObject):
    """Worker za učitavanje podataka iz Google Sheets u pozadini"""
    progress = pyqtSignal(int, str)  # progress percentage, status message
    finished = pyqtSignal(dict)  # {sheet_name: all_values}
    error = pyqtSignal(str)
    
    def __init__(self, workbook, sheet_names):
        super().__init__()
        self.workbook = workbook
        self.sheet_names = sheet_names
        self._cancelled = False
        self._mutex = QMutex()
    
    def cancel(self):
        self._mutex.lock()
        self._cancelled = True
        self._mutex.unlock()
    
    def is_cancelled(self):
        self._mutex.lock()
        cancelled = self._cancelled
        self._mutex.unlock()
        return cancelled
    
    def run(self):
        try:
            data = {}
            total_sheets = len(self.sheet_names)
            
            for idx, sheet_name in enumerate(self.sheet_names):
                if self.is_cancelled():
                    return
                
                self.progress.emit(
                    int((idx / total_sheets) * 100),
                    f"Učitavanje {sheet_name}..."
                )
                
                try:
                    sheet = self.workbook.worksheet(sheet_name)
                    all_values = sheet.get_all_values()
                    data[sheet_name] = all_values
                except Exception as e:
                    print(f"Greška pri učitavanju {sheet_name}: {e}")
                    data[sheet_name] = []
            
            if not self.is_cancelled():
                self.progress.emit(100, "Učitavanje završeno")
                self.finished.emit(data)
        except Exception as e:
            self.error.emit(f"Greška pri učitavanju podataka: {str(e)}")


class PointsWriterWorker(QObject):
    """Worker za upis bodova u Google Sheets u pozadini"""
    progress = pyqtSignal(int, str)  # progress percentage, status message
    finished = pyqtSignal(bool, str)  # success, message
    error = pyqtSignal(str)
    
    def __init__(self, workbook, items, pairs):
        super().__init__()
        self.workbook = workbook
        self.items = items
        self.pairs = pairs
        self._cancelled = False
        self._mutex = QMutex()
    
    def cancel(self):
        self._mutex.lock()
        self._cancelled = True
        self._mutex.unlock()
    
    def is_cancelled(self):
        self._mutex.lock()
        cancelled = self._cancelled
        self._mutex.unlock()
        return cancelled
    
    def run(self):
        try:
            # Odredi koje worksheet-e stvarno treba na osnovu batch podataka
            sheet_names = {
                'o': "2025 Opšte",
                'h': "2025 HR",
                'p': "Projekti"
            }
            
            # Pronađi koje tipove podataka imamo u batch-u
            needed_keys = set()
            for item in self.items:
                if item and len(item) > 0:
                    key = item[0]
                    if key in sheet_names:
                        needed_keys.add(key)
            
            # Ako nema podataka, greška
            if not needed_keys:
                self.error.emit("Nema podataka za upis. Proverite da li ste izabrali aktivnost i poene.")
                return
            
            # Prvo uzmi listu svih dostupnih worksheet-a za dijagnostiku
            try:
                all_worksheets = self.workbook.worksheets()
                available_names = [ws.title for ws in all_worksheets]
            except Exception:
                available_names = []
            
            # Učitaj samo potrebne worksheet-e
            sheets = {}
            for key in needed_keys:
                sheet_name = sheet_names[key]
                try:
                    sheets[key] = self.workbook.worksheet(sheet_name)
                except WorksheetNotFound:
                    # Pripremi detaljnu poruku sa listom dostupnih worksheet-a
                    available_list = "\n".join([f"  - '{name}'" for name in available_names])
                    error_msg = (
                        f"Worksheet '{sheet_name}' ne postoji u Google Sheets dokumentu.\n\n"
                        f"Dostupni worksheet-i su:\n{available_list}\n\n"
                        f"Proverite da li ime worksheet-a tačno odgovara (razmaci, velika/mala slova)."
                    )
                    self.error.emit(error_msg)
                    return
                except Exception as e:
                    available_list = "\n".join([f"  - '{name}'" for name in available_names])
                    error_msg = (
                        f"Greška pri pristupanju worksheet-u '{sheet_name}': {str(e)}\n\n"
                        f"Dostupni worksheet-i su:\n{available_list}"
                    )
                    self.error.emit(error_msg)
                    return
            
            # Učitaj sve podatke jednom
            self.progress.emit(10, "Učitavanje podataka...")
            all_values_cache = {}
            for key, sheet in sheets.items():
                if self.is_cancelled():
                    return
                try:
                    all_values_cache[key] = sheet.get_all_values()
                except APIError as e:
                    self.error.emit(
                        f"Greška pri učitavanju podataka sa '{sheet_names[key]}' worksheet-a: {str(e)}. "
                        f"Proverite dozvole za pristup."
                    )
                    return
                except Exception as e:
                    self.error.emit(
                        f"Greška pri učitavanju podataka sa '{sheet_names[key]}' worksheet-a: {str(e)}"
                    )
                    return
            
            # Pripremi batch updates za efikasnije izvršavanje
            batch_updates = {key: [] for key in sheets.keys()}
            total_operations = len(self.pairs) * len([item for item in self.items if item])
            current_operation = 0
            
            self.progress.emit(30, "Priprema upisa...")
            
            for name, points in self.pairs:
                if self.is_cancelled():
                    return
                
                for item in self.items:
                    if not item:
                        continue
                    
                    key = item[0]
                    if key not in sheets:
                        continue
                    
                    sheet = sheets[key]
                    all_values = all_values_cache[key]
                    
                    result = self._find_and_write(item, sheet, all_values, name)
                    if result is None:
                        print(f"Greška prilikom pronalaska pozicije za osobu {name}!")
                        continue
                    
                    row, col = result
                    try:
                        # Umesto direktnog update-a, pripremi batch update
                        cell_range = rowcol_to_a1(row, col + 1)
                        try:
                            cell_val = float(sheet.cell(row, col + 1).value)
                        except (ValueError, TypeError):
                            cell_val = 0.0
                        
                        # Upisuj kao broj (float), ne kao string, da bi SUM funkcija radila
                        value_to_update = cell_val + float(points)
                        batch_updates[key].append({
                            'range': cell_range,
                            'values': [[value_to_update]]
                        })
                    except Exception as e:
                        print(f"Greška prilikom pripreme upisa za osobu {name}: {e}")
                    
                    current_operation += 1
                    progress = 30 + int((current_operation / total_operations) * 60)
                    self.progress.emit(
                        progress,
                        f"Upis bodova za {name}... ({current_operation}/{total_operations})"
                    )
            
            # Izvrši batch updates
            if not self.is_cancelled():
                self.progress.emit(90, "Upisivanje u Google Sheets...")
                for key, updates in batch_updates.items():
                    if updates and not self.is_cancelled():
                        try:
                            sheets[key].batch_update(updates)
                        except APIError as e:
                            sheet_name = sheet_names.get(key, key)
                            self.error.emit(
                                f"Greška pri upisu u '{sheet_name}' worksheet: {str(e)}. "
                                f"Proverite dozvole za pisanje u Google Sheets."
                            )
                            return
                        except Exception as e:
                            sheet_name = sheet_names.get(key, key)
                            print(f"Greška pri batch update-u za {sheet_name}: {e}")
                            self.error.emit(
                                f"Greška pri upisu u '{sheet_name}' worksheet: {str(e)}"
                            )
                            return
                
                if not self.is_cancelled():
                    self.progress.emit(100, "Upis završen")
                    self.finished.emit(True, f"Uspešno upisano {len(self.pairs)} osoba")
        except WorksheetNotFound as e:
            self.error.emit(
                f"Worksheet '{str(e)}' ne postoji u Google Sheets dokumentu. "
                f"Proverite da li svi potrebni worksheet-i postoje."
            )
        except APIError as e:
            self.error.emit(
                f"Greška Google Sheets API-ja: {str(e)}. "
                f"Proverite internet konekciju i dozvole za pristup."
            )
        except Exception as e:
            error_type = type(e).__name__
            self.error.emit(
                f"Greška pri upisu bodova ({error_type}): {str(e)}"
            )
    
    def _find_and_write(self, item, sheet, all_values, name):
        """Helper metoda za pronalaženje pozicije - kopija iz upis.py"""
        result = []
        
        if item[1] == 'Aktivacija u godišnjim timovima' or item[1] == 'Radne grupe':
            limit = 31
            dokle = 4
        else:
            limit = 11
            dokle = 3
        
        for i in range(1, dokle):
            found = False
            search_words = set(re.split(r"[ /]+", normalize_name(item[i])))
            
            if item[0] == 'p':
                start_value = 1 if i == 1 else 3
            else:
                start_value = 2 if i == 1 else 3 if i == 2 else 4
            
            for row_idx, row in enumerate(all_values[start_value:], start=start_value):
                if found:
                    break
                
                if item[0] == 'o':
                    if result:
                        if i in [2, 3]:
                            valid_cols = [col for _, col in reversed(result) if col is not None]
                            start_col = valid_cols[0] if valid_cols else 0
                        else:
                            start_col = 0
                    else:
                        start_col = 0
                else:
                    start_col = result[0][1] if result and result[0][1] is not None else 0
                
                if item[1] == 'Radne grupe' and i == 2:
                    search_words = set(re.split(r"[ /]+", normalize_name(item[3])))
                
                if result == []:
                    limit = 1000
                
                for col_idx, cell in enumerate(row[start_col:start_col + limit], start=start_col):
                    cell_words = set(re.split(r"[ /]+", normalize_name(cell)))
                    if search_words.issubset(cell_words):
                        result.append((row_idx, col_idx))
                        found = True
                        break
                
                if self.is_cancelled():
                    return None
            
            if not found:
                result.append((None, None))
        
        try:
            cell = sheet.find(name)
            valid_results = [res for res in result if res[1] is not None]
            if not valid_results:
                return None
            return (cell.row, valid_results[-1][1])
        except:
            return None


class PointsReaderWorker(QObject):
    """Worker za čitanje bodova pojedinačne osobe iz Google Sheets"""
    finished = pyqtSignal(dict)  # {hr, opste, projekti, ukupno, status}
    error = pyqtSignal(str)
    
    def __init__(self, workbook, name):
        super().__init__()
        self.workbook = workbook
        self.name = name
    
    def run(self):
        try:
            sheet = self.workbook.worksheet('ZBIR')
            all_values = sheet.get_all_values()
            
            name_col_idx = 1
            row_idx = None
            
            for i, row in enumerate(all_values[1:], start=2):
                if len(row) > name_col_idx and row[name_col_idx] == self.name:
                    row_idx = i
                    break
            
            if row_idx is None:
                self.error.emit(f"Osoba {self.name} nije pronađena u bazi")
                return
            
            row_data = all_values[row_idx - 1]
            
            result = {
                'hr': row_data[2] if len(row_data) > 2 else "0",
                'opste': row_data[3] if len(row_data) > 3 else "0",
                'projekti': row_data[4] if len(row_data) > 4 else "0",
                'ukupno': row_data[6] if len(row_data) > 6 else "0",
                'status': row_data[7] if len(row_data) > 7 else ""
            }
            
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(f"Greška pri čitanju bodova: {str(e)}")

