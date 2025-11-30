from PyQt5.QtCore import QObject, QMutex, QTimer, pyqtSignal
from datetime import datetime, timedelta
import threading


class CacheManager(QObject):
    """Thread-safe cache manager za Google Sheets podatke"""
    cache_updated = pyqtSignal(str)  # sheet_name
    cache_invalidated = pyqtSignal(str)  # sheet_name
    
    def __init__(self, refresh_interval_minutes=5):
        super().__init__()
        self._cache = {}
        self._cache_timestamps = {}
        self._mutex = QMutex()
        self.refresh_interval = timedelta(minutes=refresh_interval_minutes)
        
        # Timer za automatski refresh
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._auto_refresh_check)
        self.refresh_timer.start(60000)  # Proverava svakih 60 sekundi
    
    def _auto_refresh_check(self):
        """Proverava da li je potreban refresh cache-a"""
        self._mutex.lock()
        try:
            now = datetime.now()
            for sheet_name, timestamp in list(self._cache_timestamps.items()):
                if now - timestamp > self.refresh_interval:
                    # Cache je zastareo, invalidiraj ga
                    if sheet_name in self._cache:
                        del self._cache[sheet_name]
                    del self._cache_timestamps[sheet_name]
                    self.cache_invalidated.emit(sheet_name)
        finally:
            self._mutex.unlock()
    
    def get_cached_data(self, sheet_name):
        """Dobija keširane podatke za dati sheet"""
        self._mutex.lock()
        try:
            if sheet_name in self._cache:
                timestamp = self._cache_timestamps.get(sheet_name)
                if timestamp and datetime.now() - timestamp < self.refresh_interval:
                    return self._cache[sheet_name]
            return None
        finally:
            self._mutex.unlock()
    
    def update_cache(self, sheet_name, data):
        """Ažurira cache za dati sheet"""
        self._mutex.lock()
        try:
            self._cache[sheet_name] = data
            self._cache_timestamps[sheet_name] = datetime.now()
            self.cache_updated.emit(sheet_name)
        finally:
            self._mutex.unlock()
    
    def invalidate_cache(self, sheet_name=None):
        """Invalidira cache za dati sheet ili sve ako sheet_name nije naveden"""
        self._mutex.lock()
        try:
            if sheet_name:
                if sheet_name in self._cache:
                    del self._cache[sheet_name]
                if sheet_name in self._cache_timestamps:
                    del self._cache_timestamps[sheet_name]
                self.cache_invalidated.emit(sheet_name)
            else:
                # Invalidiraj sve
                invalidated = list(self._cache.keys())
                self._cache.clear()
                self._cache_timestamps.clear()
                for name in invalidated:
                    self.cache_invalidated.emit(name)
        finally:
            self._mutex.unlock()
    
    def is_cached(self, sheet_name):
        """Proverava da li su podaci keširani i validni"""
        self._mutex.lock()
        try:
            if sheet_name not in self._cache:
                return False
            timestamp = self._cache_timestamps.get(sheet_name)
            if not timestamp:
                return False
            return datetime.now() - timestamp < self.refresh_interval
        finally:
            self._mutex.unlock()
    
    def get_cache_age(self, sheet_name):
        """Vraća starost cache-a u sekundama"""
        self._mutex.lock()
        try:
            if sheet_name not in self._cache_timestamps:
                return None
            age = datetime.now() - self._cache_timestamps[sheet_name]
            return age.total_seconds()
        finally:
            self._mutex.unlock()
    
    def clear_all(self):
        """Briše sav cache"""
        self.invalidate_cache()

