"""
Konfigurace logování pro MedDocAI Anonymizer
"""
import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

class LoggerSetup:
    """Třída pro nastavení logování"""
    
    @staticmethod
    def setup_logger(
        name: str,
        log_file: Optional[str] = None,
        level: int = logging.INFO,
        format_string: Optional[str] = None
    ) -> logging.Logger:
        """
        Nastavení loggeru s rotačními soubory a konzole výstupem
        
        Args:
            name: Název loggeru
            log_file: Cesta k log souboru (volitelné)
            level: Level logování
            format_string: Formát zpráv (volitelné)
        
        Returns:
            Nakonfigurovaný logger
        """
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # Pokud logger už má handlery, vrátíme ho
        if logger.handlers:
            return logger
        
        # Výchozí formát
        if format_string is None:
            format_string = (
                '%(asctime)s - %(name)s - %(levelname)s - '
                '%(filename)s:%(lineno)d - %(message)s'
            )
        
        formatter = logging.Formatter(format_string)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler s rotací (pokud je zadán soubor)
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger

class ApplicationLogger:
    """Centrální správce loggerů pro aplikaci"""
    
    def __init__(self, log_dir: Path):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Hlavní application logger
        self.app_logger = LoggerSetup.setup_logger(
            name="meddocai.app",
            log_file=str(self.log_dir / "application.log"),
            level=logging.INFO
        )
        
        # Logger pro anonymizaci
        self.anonymization_logger = LoggerSetup.setup_logger(
            name="meddocai.anonymization",
            log_file=str(self.log_dir / "anonymization.log"),
            level=logging.INFO
        )
        
        # Logger pro bezpečnost
        self.security_logger = LoggerSetup.setup_logger(
            name="meddocai.security",
            log_file=str(self.log_dir / "security.log"),
            level=logging.WARNING
        )
        
        # Logger pro performance
        self.performance_logger = LoggerSetup.setup_logger(
            name="meddocai.performance",
            log_file=str(self.log_dir / "performance.log"),
            level=logging.INFO
        )
        
        # Logger pro chyby
        self.error_logger = LoggerSetup.setup_logger(
            name="meddocai.errors",
            log_file=str(self.log_dir / "errors.log"),
            level=logging.ERROR
        )
    
    def log_anonymization_start(self, filename: str, method: str):
        """Zalogování začátku anonymizace"""
        self.anonymization_logger.info(
            f"Začíná anonymizace souboru: {filename}, metoda: {method}"
        )
    
    def log_anonymization_complete(self, filename: str, entities_found: int, duration: float):
        """Zalogování dokončení anonymizace"""
        self.anonymization_logger.info(
            f"Anonymizace dokončena: {filename}, "
            f"nalezeno entit: {entities_found}, "
            f"trvání: {duration:.2f}s"
        )
        
        self.performance_logger.info(
            f"Performance - Anonymizace: {filename}, "
            f"entity: {entities_found}, čas: {duration:.2f}s"
        )
    
    def log_security_event(self, event_type: str, details: str):
        """Zalogování bezpečnostní události"""
        self.security_logger.warning(f"{event_type}: {details}")
    
    def log_error(self, error: Exception, context: str = ""):
        """Zalogování chyby"""
        self.error_logger.error(
            f"Chyba v kontextu '{context}': {type(error).__name__}: {str(error)}",
            exc_info=True
        )
    
    def log_upload(self, filename: str, file_size: int, user_ip: str = "unknown"):
        """Zalogování uploadu souboru"""
        self.app_logger.info(
            f"Upload souboru: {filename}, "
            f"velikost: {file_size} bytes, "
            f"IP: {user_ip}"
        )
    
    def log_export(self, filename: str, export_format: str):
        """Zalogování exportu"""
        self.app_logger.info(
            f"Export souboru: {filename}, formát: {export_format}"
        )

# Singleton instance
_logger_instance: Optional[ApplicationLogger] = None

def get_logger(log_dir: Optional[Path] = None) -> ApplicationLogger:
    """Získání singleton instance loggeru"""
    global _logger_instance
    
    if _logger_instance is None:
        if log_dir is None:
            log_dir = Path("logs")
        _logger_instance = ApplicationLogger(log_dir)
    
    return _logger_instance

def setup_production_logging():
    """Nastavení logování pro produkci"""
    # Nastavení root logger pro production
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.WARNING)
    
    # Potlačení debug zpráv z externích knihoven
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("streamlit").setLevel(logging.WARNING)
    logging.getLogger("presidio_analyzer").setLevel(logging.WARNING)
