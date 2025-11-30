import logging
from datetime import datetime
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal


class ErrorHandler(QObject):
    """Centralizovani error handler sa logging i user-friendly porukama"""
    error_occurred = pyqtSignal(str, str)  # error_type, user_message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('spc_errors.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('SPC')
    
    def handle_error(self, error, context="", show_user=True, retry_callback=None):
        """
        Centralizovana metoda za rukovanje greškama
        
        Args:
            error: Exception objekat ili string poruka
            context: Kontekst gde se greška desila
            show_user: Da li da prikaže poruku korisniku
            retry_callback: Callback funkcija za retry (opciono)
        """
        error_message = str(error) if isinstance(error, Exception) else error
        error_type = type(error).__name__ if isinstance(error, Exception) else "Error"
        
        # Loguj grešku
        self.logger.error(
            f"{context}: {error_type} - {error_message}",
            exc_info=isinstance(error, Exception)
        )
        
        # Konvertuj u user-friendly poruku
        user_message = self._get_user_friendly_message(error, context)
        
        # Emituj signal
        self.error_occurred.emit(error_type, user_message)
        
        # Prikaži korisniku ako je potrebno
        if show_user:
            self._show_error_dialog(user_message, retry_callback)
        
        return user_message
    
    def _get_user_friendly_message(self, error, context):
        """Konvertuje tehničke greške u user-friendly poruke"""
        error_str = str(error).lower()
        
        # Network greške
        if "network" in error_str or "connection" in error_str or "timeout" in error_str:
            return "Problem sa internet konekcijom. Proverite konekciju i pokušajte ponovo."
        
        # Authentication greške
        if "auth" in error_str or "credential" in error_str or "permission" in error_str:
            return "Problem sa autentifikacijom. Proverite credentials.json fajl."
        
        # Google API greške
        if "quota" in error_str or "rate limit" in error_str:
            return "Prekoračen je limit zahteva ka Google Sheets API-ju. Sačekajte malo i pokušajte ponovo."
        
        # Sheet not found
        if "not found" in error_str or "worksheet" in error_str:
            return "Traženi sheet nije pronađen. Proverite da li sheet postoji u Google Sheets dokumentu."
        
        # Generic greška
        if context:
            return f"Greška u {context}: {str(error)[:100]}"
        return f"Desila se greška: {str(error)[:100]}"
    
    def _show_error_dialog(self, message, retry_callback=None):
        """Prikazuje error dialog korisniku"""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Greška")
        msg_box.setText(message)
        
        if retry_callback:
            retry_button = msg_box.addButton("Pokušaj ponovo", QMessageBox.ActionRole)
            cancel_button = msg_box.addButton("Otkaži", QMessageBox.RejectRole)
            msg_box.exec_()
            
            if msg_box.clickedButton() == retry_button:
                retry_callback()
        else:
            msg_box.addButton("OK", QMessageBox.AcceptRole)
            msg_box.exec_()
    
    def handle_network_error(self, error, retry_callback=None):
        """Specijalizovana metoda za network greške sa retry logikom"""
        return self.handle_error(
            error,
            context="Network operacija",
            show_user=True,
            retry_callback=retry_callback
        )
    
    def handle_sheet_error(self, error, sheet_name="", retry_callback=None):
        """Specijalizovana metoda za Google Sheets greške"""
        context = f"Google Sheets operacija"
        if sheet_name:
            context += f" ({sheet_name})"
        return self.handle_error(
            error,
            context=context,
            show_user=True,
            retry_callback=retry_callback
        )
    
    def log_info(self, message):
        """Loguje informativnu poruku"""
        self.logger.info(message)
    
    def log_warning(self, message):
        """Loguje upozorenje"""
        self.logger.warning(message)


# Globalna instanca error handlera
_error_handler_instance = None


def get_error_handler():
    """Dobija globalnu instancu error handlera"""
    global _error_handler_instance
    if _error_handler_instance is None:
        _error_handler_instance = ErrorHandler()
    return _error_handler_instance

