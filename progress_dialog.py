from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal


class ProgressDialog(QDialog):
    """Progress dialog sa mogućnošću otkazivanja operacija"""
    cancelled = pyqtSignal()
    
    def __init__(self, parent=None, title="U toku...", show_cancel=True):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(400)
        self._cancelled = False
        
        layout = QVBoxLayout()
        
        # Status label
        self.status_label = QLabel("Priprema...")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        if show_cancel:
            self.cancel_button = QPushButton("Otkaži")
            self.cancel_button.clicked.connect(self.on_cancel)
            button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Spreči zatvaranje prozora klikom na X dok operacija traje
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
    
    def on_cancel(self):
        """Handler za cancel dugme"""
        self._cancelled = True
        self.cancel_button.setEnabled(False)
        self.status_label.setText("Prekidanje operacije...")
        self.cancelled.emit()
    
    def update_progress(self, percentage, message=""):
        """Ažurira progress bar i status poruku"""
        self.progress_bar.setValue(percentage)
        if message:
            self.status_label.setText(message)
    
    def set_status(self, message):
        """Postavlja status poruku"""
        self.status_label.setText(message)
    
    def is_cancelled(self):
        """Proverava da li je operacija otkazana"""
        return self._cancelled
    
    def finish(self, success=True, message=""):
        """Završava dialog sa porukom"""
        if success:
            self.status_label.setText(message or "Uspešno završeno!")
            self.progress_bar.setValue(100)
        else:
            self.status_label.setText(message or "Greška!")
        
        # Omogući zatvaranje
        self.setWindowFlags(Qt.Dialog)
        if hasattr(self, 'cancel_button'):
            self.cancel_button.setText("Zatvori")
            self.cancel_button.setEnabled(True)
            self.cancel_button.clicked.disconnect()
            self.cancel_button.clicked.connect(self.accept)
        else:
            # Ako nema cancel dugme, dodaj close dugme
            button_layout = self.layout().itemAt(2).layout()
            close_button = QPushButton("Zatvori")
            close_button.clicked.connect(self.accept)
            button_layout.addWidget(close_button)
    
    def closeEvent(self, event):
        """Spreči zatvaranje dok operacija traje"""
        if not self._cancelled and self.progress_bar.value() < 100:
            # Dozvoli zatvaranje samo ako je operacija završena ili otkazana
            event.ignore()
        else:
            event.accept()

