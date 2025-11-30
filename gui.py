import sys
import unicodedata
import difflib
from gspread.utils import rowcol_to_a1
import gspread
from qt import Ui_MainWindow
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QCompleter, QMessageBox, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QComboBox, QPushButton, QScrollArea, QDialog
)

from PyQt5.QtWidgets import QMainWindow, QCompleter
from PyQt5.QtCore import QStringListModel, Qt, QTimer, QThread
from rolesOpste import rolesOpsteDict
from rolesHR import rolesHRDict
from rolesProjekti import rolesProjektiDict

from updateDropDown import update_dropdown
from dropDownFunctions import clear_all_dropdowns, get_data, get_points_for_activity

# Asinhrono programiranje komponente
from workers import PointsWriterWorker, PointsReaderWorker, SheetDataLoaderWorker
from progress_dialog import ProgressDialog
from cache_manager import CacheManager
from error_handler import get_error_handler
from sheetConnection import _lazy_connection, workbook

# Backward compatibility - biće popunjeno asinhrono
names_list = []
original_names_list = []
normalized_names_list = []


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
        if all(value != "" for value in values):
            self.accept()
            return values
        else:
            QMessageBox.warning(self, "Upozorenje", "Niste upisali poene za sve osobe!")
            return None
            
# class SubstringCompleter(QCompleter):
#     def __init__(self, completions, parent=None):
#         super().__init__(completions, parent)
#         self.setCaseSensitivity(Qt.CaseInsensitive)
#         self.setFilterMode(Qt.MatchContains)  # Match any part of the string
#         self.setModel(QStringListModel(completions))
def normalize_name(input_str):
    if not isinstance(input_str, str):
        return ""
    text = input_str.lower().strip()
    replacements = {
        'č': 'c',
        'ć': 'c',
        'đ': 'dj',
        'š': 's',
        'ž': 'z',
        'á': 'a',
        'é': 'e',
        'í': 'i',
        'ó': 'o',
        'ú': 'u',
        'ü': 'u'
    }
    for src, target in replacements.items():
        text = text.replace(src, target)
    text = unicodedata.normalize('NFD', text)
    return ''.join(c for c in text if unicodedata.category(c) != 'Mn')

# 2. Custom Completer
class FuzzyCompleter(QCompleter):
    def __init__(self, original_names, normalized_names, parent=None):
        super().__init__(parent)
        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.setFilterMode(Qt.MatchContains)
        
        self.original_names = original_names
        self.normalized_names = normalized_names
        
        self.model = QStringListModel()
        self.setModel(self.model)

    def updateModel(self, user_input):
        # Normalize the user input
        norm_input = normalize_name(user_input)

        # Substring matches
        substring_matches = [
            original for original, norm in zip(self.original_names, self.normalized_names)
            if norm_input in norm
        ]

        # Fuzzy matches
        fuzzy_matches = difflib.get_close_matches(norm_input, self.normalized_names, n=10, cutoff=0.6)
        fuzzy_originals = [
            original for original, norm in zip(self.original_names, self.normalized_names)
            if norm in fuzzy_matches
        ]

        # Combine and deduplicate matches
        combined = list(dict.fromkeys(substring_matches + fuzzy_originals))

        # Update the model with the original names of the matches
        self.model.setStringList(combined)

    def splitPath(self, path):
        # Update the model whenever the user types something
        self.updateModel(path)
        return [path]

class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.stackedWidget.setCurrentIndex(0)
        self.allPersonsRight.setReadOnly(True)
        self.completer_activated = False
        
        # Inicijalizuj cache manager i error handler
        self.cache_manager = CacheManager(refresh_interval_minutes=5)
        self.error_handler = get_error_handler()
        
        # Worker threads
        self._current_worker_thread = None
        self._current_progress_dialog = None

        '''OVO SE POZIVA KAD JE POTREBNO UPDATE-OVATI UKUPAN BROJ BODOVA - KARTICA ZBIR'''
        # self.updateTotalPoints()

        # Name completer - inicijalno prazan, biće ažuriran kada se učitaju imena
        completer = FuzzyCompleter([], [])
        self.nameLineEditLeft.setCompleter(completer)
        self.namesRightLineEdit.setCompleter(completer)
        self.namesRightLineEdit.completer().activated.connect(self.onCompleterActivatedRight)
        
        # Pokreni asinhrono učitavanje names_list
        self._load_names_async()
        
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
        #self.namesRightLineEdit.completer().activated.connect(self.onCompleterActivated)
        self.upisiButtonLeft.clicked.connect(self.onUpisiButtonLeftClicked)
        self.addButtonRight.clicked.connect(self.onAddButtonRIghtClicked)
        self.namesRightLineEdit.update()
        self.namesRightLineEdit.returnPressed.connect(self.onAddButtonRIghtClicked)
        #self.namesRightLineEdit.update()
        self.showPointsButton.clicked.connect(self.onShowPointsButtonClicked)

        # Deleting last added name or selected name
        self.removeNameButton.clicked.connect(self.onRemoveNameClicked)
    
    def _load_names_async(self):
        """Asinhrono učitava names_list pri startu aplikacije"""
        def on_names_loaded(names, original_names, normalized_names):
            global names_list, original_names_list, normalized_names_list
            names_list = names
            original_names_list = original_names
            normalized_names_list = normalized_names
            
            # Ažuriraj completer-e
            completer_left = FuzzyCompleter(original_names_list, normalized_names_list)
            completer_right = FuzzyCompleter(original_names_list, normalized_names_list)
            self.nameLineEditLeft.setCompleter(completer_left)
            self.namesRightLineEdit.setCompleter(completer_right)
            self.namesRightLineEdit.completer().activated.connect(self.onCompleterActivatedRight)
        
        def on_connection_error(error_msg):
            self.error_handler.handle_error(error_msg, context="Učitavanje imena")
        
        # Poveži signale
        _lazy_connection.names_loaded.connect(on_names_loaded)
        _lazy_connection.connection_error.connect(on_connection_error)
        
        # Pokreni učitavanje u worker thread-u
        thread = QThread()
        worker = _lazy_connection
        worker.moveToThread(thread)
        
        thread.started.connect(worker.load_names_async)
        thread.start()
        
        # Čuvaj referencu na thread
        self._names_load_thread = thread

    def clearLineEdit(self):
        self.namesRightLineEdit.clear()
        self.namesRightLineEdit.repaint()
        self.namesRightLineEdit.update()
        self.namesRightLineEdit.setFocus()

    def onCompleterActivatedRight(self, text):
        self.namesRightLineEdit.returnPressed.disconnect(self.onAddButtonRIghtClicked)

        names = self.return_names()
        if text in names_list and text not in names:
            self.completer_activated = True
            self.allPersonsRight.appendPlainText(text)
            QTimer.singleShot(0, self.clearLineEdit)
        else:
            QTimer.singleShot(0, self.clearLineEdit)

        self.namesRightLineEdit.returnPressed.connect(self.onAddButtonRIghtClicked)

    def onAddButtonRIghtClicked(self):
        if self.completer_activated:
            self.completer_activated = False
            return

        names = self.return_names()
        name = self.namesRightLineEdit.text()
        if name in names_list and name not in names:
            self.allPersonsRight.appendPlainText(name)
            QTimer.singleShot(0, self.clearLineEdit)
        else:
            QTimer.singleShot(0, self.clearLineEdit)
            QMessageBox.warning(self, "Upozorenje", "Ime ne postoji u bazi ili je već dodato")

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
        return (self.dropDownHR3.isEnabled() and self.dropDownHR3.currentText()) or (self.dropDownOpste4.isEnabled() and self.dropDownOpste4.currentText()) or (self.dropDownProjekti3.isEnabled() and self.dropDownProjekti3.currentText())

    def return_names(self):
        addedNames = self.allPersonsRight.toPlainText()
        names = addedNames.split('\n')
        return names

    def onUpisiButtonLeftClicked(self):
        opsteData = get_data(window=self, type='o')
        HRData = get_data(window=self, type='h')
        projektiData = get_data(window=self, type='p')
        names = self.return_names()
        batch = [opsteData, HRData, projektiData]
        check = self.proveri(batch, names)
        
        if not names:
            QMessageBox.warning(self, "Greška", "Dodaj ime za upis!")
            return
        
        if check and self.upisani_poeni():
            print("proslo provere, batch: ", batch)
            points = [b[-1] for b in batch if b]
            pairs = [(name, point) for name in names for point in points]
            self._upisi_async(batch, pairs)
        else:
            if not self.allPersonsRight.toPlainText().strip() == '': 
                popup = NameDropdownPopup(names, self)
                if popup.exec_() == QDialog.Accepted:
                    points = popup.submit()
                    if points:
                        pairs = list(zip(names, points))
                        print('parovi = ', pairs)
                        self._upisi_async(batch, pairs)
            else:
                QMessageBox.warning(self, "Greška", "Dodaj ime za upis!")
    
    def _upisi_async(self, batch, pairs):
        """Asinhrono upisuje bodove koristeći PointsWriterWorker"""
        # Kreiraj progress dialog
        progress_dialog = ProgressDialog(
            self, 
            title="Upis bodova", 
            show_cancel=True
        )
        self._current_progress_dialog = progress_dialog
        
        # Kreiraj worker i thread
        worker = PointsWriterWorker(workbook, batch, pairs)
        thread = QThread()
        worker.moveToThread(thread)
        
        # Poveži signale
        def on_progress(percentage, message):
            progress_dialog.update_progress(percentage, message)
        
        def on_finished(success, message):
            thread.quit()
            thread.wait()
            progress_dialog.finish(success, message)
            self._current_progress_dialog = None
            self._current_worker_thread = None
            
            if success:
                QMessageBox.information(self, "Uspeh", message)
                self.allPersonsRight.clear()
                clear_all_dropdowns(self)
                self.dropDownOpste1.addItems(rolesOpsteDict.keys())
                self.dropDownHR1.addItems(rolesHRDict.keys())
                self.dropDownProjekti1.addItems(rolesProjektiDict.keys())
                # Invalidiraj cache nakon upisa
                self.cache_manager.invalidate_cache()
            else:
                self.error_handler.handle_error(message, context="Upis bodova")
        
        def on_error(error_msg):
            thread.quit()
            thread.wait()
            progress_dialog.finish(False, error_msg)
            self._current_progress_dialog = None
            self._current_worker_thread = None
            self.error_handler.handle_error(error_msg, context="Upis bodova")
        
        def on_cancel():
            worker.cancel()
        
        thread.started.connect(worker.run)
        worker.progress.connect(on_progress)
        worker.finished.connect(on_finished)
        worker.error.connect(on_error)
        progress_dialog.cancelled.connect(on_cancel)
        
        # Pokreni thread
        thread.start()
        self._current_worker_thread = thread
        
        # Prikaži progress dialog
        progress_dialog.exec_()
    
    def get_selected_type(self):
        if self.dropDownOpste1.isEnabled():
            return 'o'
        if self.dropDownHR1.isEnabled():
            return 'h'
        if self.dropDownProjekti1.isEnabled():
            return 'p'
        return None
    
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
        clear_all_dropdowns(self)
        self.namesRightLineEdit.clear()
        self.dropDownOpste1.addItems(rolesOpsteDict.keys())
        self.dropDownHR1.addItems(rolesHRDict.keys())
        self.dropDownProjekti1.addItems(rolesProjektiDict.keys())
        self.enable_all_first_dropdowns()
        self.stackedWidget.setCurrentIndex(0)
    
    def onShowPointsButtonClicked(self):
        name = self.nameLineEditLeft.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Greška", "Unesite ime osobe!")
            return
        
        if name not in names_list:
            QMessageBox.warning(self, "Greška", "Ime ne postoji u bazi!")
            return
        
        # Proveri cache prvo
        cached_data = self.cache_manager.get_cached_data('ZBIR')
        
        if cached_data:
            # Koristi cache
            self._display_points_from_data(name, cached_data)
        else:
            # Učitaj asinhrono
            self._load_points_async(name)
    
    def _display_points_from_data(self, name, all_values):
        """Prikazuje bodove iz već učitane liste podataka"""
        name_col_idx = 1
        
        row_idx = None
        for i, row in enumerate(all_values[1:], start=2):
            if len(row) > name_col_idx and row[name_col_idx] == name:
                row_idx = i
                break
        
        if row_idx is None:
            QMessageBox.warning(self, "Greška", f"Osoba {name} nije pronađena u bazi")
            return
        
        row_data = all_values[row_idx - 1]
        
        HRBodovi = row_data[2] if len(row_data) > 2 else "0"
        opsteBodovi = row_data[3] if len(row_data) > 3 else "0"
        projektiBodovi = row_data[4] if len(row_data) > 4 else "0"
        ukupnoBodova = row_data[6] if len(row_data) > 6 else "0"
        status = row_data[7] if len(row_data) > 7 else ""
        
        self.statusLabel.setText(status)
        self.bodoviLabel.setText(ukupnoBodova)
        self.opsteLabel.setText(opsteBodovi)
        self.projektiLabel.setText(projektiBodovi)
        self.hrLabel.setText(HRBodovi)
    
    def _load_points_async(self, name):
        """Asinhrono učitava bodove koristeći PointsReaderWorker"""
        # Kreiraj worker i thread
        worker = PointsReaderWorker(workbook, name)
        thread = QThread()
        worker.moveToThread(thread)
        
        # Loading indikator
        loading_label = QLabel("Učitavanje bodova...", self)
        loading_label.setStyleSheet("background-color: rgba(255, 255, 255, 200); padding: 10px;")
        loading_label.setAlignment(Qt.AlignCenter)
        loading_label.setGeometry(50, 250, 200, 30)
        loading_label.show()
        
        def on_finished(result):
            thread.quit()
            thread.wait()
            loading_label.hide()
            loading_label.deleteLater()
            self._current_worker_thread = None
            
            # Ažuriraj UI
            self.statusLabel.setText(result.get('status', ''))
            self.bodoviLabel.setText(result.get('ukupno', '0'))
            self.opsteLabel.setText(result.get('opste', '0'))
            self.projektiLabel.setText(result.get('projekti', '0'))
            self.hrLabel.setText(result.get('hr', '0'))
            
            # Ažuriraj cache
            # Učitaj ceo ZBIR sheet za cache
            try:
                sheet = workbook.worksheet('ZBIR')
                all_values = sheet.get_all_values()
                self.cache_manager.update_cache('ZBIR', all_values)
            except Exception as e:
                print(f"Greška pri ažuriranju cache-a: {e}")
        
        def on_error(error_msg):
            thread.quit()
            thread.wait()
            loading_label.hide()
            loading_label.deleteLater()
            self._current_worker_thread = None
            self.error_handler.handle_error(error_msg, context="Učitavanje bodova")
        
        thread.started.connect(worker.run)
        worker.finished.connect(on_finished)
        worker.error.connect(on_error)
        
        # Pokreni thread
        thread.start()
        self._current_worker_thread = thread

    def updateTotalPoints(self):
        zbirSheet = workbook.worksheet('ZBIR')
        sheets = [
            '2025 Opšte', '2024 Opšte', '2023 Opšte', '2022 Opšte', '2021 Opšte',
            '2025 HR', '2024 HR', '2023 HR', '2022 HR', 'Projekti'
        ]

        updates = []

        # Load full ZBIR sheet once (names in column 2)
        zbir_data = zbirSheet.get_all_values()
        zbir_name_to_row = {row[1]: idx + 1 for idx, row in enumerate(zbir_data) if len(row) >= 2 and row[1]}

        # Load all other sheets completely (names in column 2)
        sheet_data = {}
        for sheet_name in sheets:
            try:
                sheet = workbook.worksheet(sheet_name)
                data = sheet.get_all_values()
                name_to_row = {row[1]: row for row in data if len(row) >= 2 and row[1]}
                sheet_data[sheet_name] = name_to_row
            except Exception as e:
                print(f"Error loading sheet {sheet_name}: {e}")

        for name in names_list:
            try:
                if name not in zbir_name_to_row:
                    print(f"{name} not found in ZBIR sheet, skipping.")
                    continue

                zbir_row = zbir_name_to_row[name]
                old_value = (
                    float(zbir_data[zbir_row - 1][9]) 
                    if len(zbir_data[zbir_row - 1]) >= 10 and zbir_data[zbir_row - 1][9] 
                    else 0
                )

                totalPoints = 0
                for sheet_name in sheets:
                    row = sheet_data.get(sheet_name, {}).get(name)
                    if row and len(row) >= 3 and row[2]:
                        try:
                            totalPoints += float(row[2])
                        except ValueError:
                            continue

                # Prepare update
                cell_range = rowcol_to_a1(zbir_row, 10)
                updates.append({
                    'range': cell_range,
                    'values': [[totalPoints]]
                })

                print(f"{name}: old = {old_value}, new = {totalPoints}")

            except Exception as e:
                print(f"Error processing {name}: {e}")

        # Batch update
        if updates:
            zbirSheet.batch_update(updates)
            print(f"✅ Batch updated {len(updates)} users.")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
