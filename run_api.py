#!/usr/bin/env python3
"""
Spouštěč pro REST API serveru MedDocAI Anonymizer
"""
import os
import sys
from pathlib import Path

# Přidání root directory do Python path
root_path = Path(__file__).parent
sys.path.append(str(root_path))

def main():
    """Hlavní funkce pro spuštění API"""
    
    print("🔗 Spouštím MedDocAI Anonymizer REST API...")
    print("📁 Používám novou modulární strukturu")
    
    try:
        from config.settings import ConfigManager
        config = ConfigManager.get_config()
        
        api_port = 8502  # Port pro API server s Swagger dokumentací
        print(f"🌐 API bude dostupné na: http://{config.host}:{api_port}")
        print(f"📖 Swagger dokumentace: http://{config.host}:{api_port}/docs")
        print(f"🔧 Prostředí: {config.environment}")
        
        # Import a spuštění
        import uvicorn
        from api.main import app
        
        if config.debug:
            # Pro development používáme reload s import string
            uvicorn.run(
                "api.main:app",
                host=config.host,
                port=api_port,
                reload=True,
                log_level="debug"
            )
        else:
            # Pro production bez reload
            uvicorn.run(
                app,
                host=config.host,
                port=api_port,
                reload=False,
                log_level="info"
            )
        
    except ImportError as e:
        print(f"❌ Chyba při importu: {e}")
        print("💡 Ujistěte se, že jsou nainstalovány všechny závislosti: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Chyba při spouštění API: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
