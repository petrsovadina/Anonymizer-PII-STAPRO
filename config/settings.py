"""
Konfigurační systém pro různá prostředí (development, production, testing)
"""
import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    """Konfigurace databáze (pro budoucí rozšíření)"""
    host: str = "localhost"
    port: int = 5432
    database: str = "meddocai"
    username: str = "postgres"
    password: str = ""

@dataclass
class SecurityConfig:
    """Bezpečnostní konfigurace"""
    secret_key: str = "default-secret-key-change-in-production"
    jwt_expiration_hours: int = 24
    max_upload_size_mb: int = 100
    allowed_file_types: list = None
    
    def __post_init__(self):
        if self.allowed_file_types is None:
            self.allowed_file_types = ['.txt', '.docx', '.pdf', '.csv']

@dataclass
class AnonymizationConfig:
    """Konfigurace anonymizace"""
    confidence_threshold: float = 0.7
    default_anonymization_method: str = "replace"
    czech_model_path: str = "cs_core_news_sm"
    max_batch_size: int = 100
    
@dataclass
class AppConfig:
    """Hlavní konfigurace aplikace"""
    environment: str = "development"
    debug: bool = True
    host: str = "localhost"
    port: int = 8501
    
    # Cesty
    base_dir: Path = Path(__file__).parent.parent
    upload_dir: Path = base_dir / "uploads"
    export_dir: Path = base_dir / "exports" 
    log_dir: Path = base_dir / "logs"
    data_dir: Path = base_dir / "data"
    
    # Sub-konfigurace
    database: DatabaseConfig = None
    security: SecurityConfig = None
    anonymization: AnonymizationConfig = None
    
    def __post_init__(self):
        if self.database is None:
            self.database = DatabaseConfig()
        if self.security is None:
            self.security = SecurityConfig()
        if self.anonymization is None:
            self.anonymization = AnonymizationConfig()
            
        # Vytvoření adresářů pokud neexistují
        for directory in [self.upload_dir, self.export_dir, self.log_dir, self.data_dir]:
            directory.mkdir(exist_ok=True)

class ConfigManager:
    """Správce konfigurace"""
    
    @staticmethod
    def get_config(environment: Optional[str] = None) -> AppConfig:
        """Získá konfiguraci pro dané prostředí"""
        env = environment or os.getenv("ENVIRONMENT", "development")
        
        if env == "production":
            return ConfigManager._get_production_config()
        elif env == "testing":
            return ConfigManager._get_testing_config()
        else:
            return ConfigManager._get_development_config()
    
    @staticmethod
    def _get_development_config() -> AppConfig:
        """Vývojová konfigurace"""
        return AppConfig(
            environment="development",
            debug=True,
            host="localhost",
            port=8501,
            security=SecurityConfig(
                secret_key="dev-secret-key",
                max_upload_size_mb=50
            ),
            anonymization=AnonymizationConfig(
                confidence_threshold=0.6,
                max_batch_size=50
            )
        )
    
    @staticmethod
    def _get_production_config() -> AppConfig:
        """Produkční konfigurace"""
        return AppConfig(
            environment="production",
            debug=False,
            host="0.0.0.0",
            port=8501,
            security=SecurityConfig(
                secret_key=os.getenv("SECRET_KEY", "change-me-in-production"),
                max_upload_size_mb=200,
                jwt_expiration_hours=12
            ),
            anonymization=AnonymizationConfig(
                confidence_threshold=0.8,
                max_batch_size=200
            )
        )
    
    @staticmethod
    def _get_testing_config() -> AppConfig:
        """Testovací konfigurace"""
        return AppConfig(
            environment="testing", 
            debug=True,
            host="localhost",
            port=8502,
            security=SecurityConfig(
                secret_key="test-secret-key",
                max_upload_size_mb=10
            ),
            anonymization=AnonymizationConfig(
                confidence_threshold=0.5,
                max_batch_size=10
            )
        )

# Globální instance konfigurace
config = ConfigManager.get_config()
