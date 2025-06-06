#!/usr/bin/env python3
"""
Spouštěcí script pro MedDocAI Anonymizer bez PyTorch chyb.
Spouští hlavní aplikaci z nové modulární struktury.
"""

import os
import sys
import warnings
from pathlib import Path

# Potlačení PyTorch warnings
warnings.filterwarnings("ignore", category=UserWarning)
os.environ["PYTHONWARNINGS"] = "ignore"

# Nastavení pro Streamlit
os.environ["STREAMLIT_SERVER_ENABLE_STATIC_SERVING"] = "true"
os.environ["STREAMLIT_SERVER_ENABLE_CORS"] = "false"

# Přidej project root do Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
os.environ["STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION"] = "false"

try:
    # Import a spuštění Streamlit s novou strukturou
    import streamlit.web.cli as stcli
    
    print("🔒 Spouštím MedDocAI Anonymizer...")
    print("📁 Používám novou modulární strukturu")
    print("🌐 Aplikace bude dostupná na: http://localhost:8501")
    
    if __name__ == '__main__':
        sys.argv = ["streamlit", "run", "app/main.py", "--server.port=8501"]
        sys.exit(stcli.main())
        
except ImportError as e:
    print(f"❌ Chyba při importu Streamlit: {e}")
    print("💡 Spusťte: pip install streamlit")
    sys.exit(1)
except Exception as e:
    print(f"❌ Neočekávaná chyba: {e}")
    sys.exit(1)
