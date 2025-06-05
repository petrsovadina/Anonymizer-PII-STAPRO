#!/usr/bin/env python3
"""
Spouštěcí script pro MedDocAI Anonymizer bez PyTorch chyb.
"""

import os
import sys
import warnings

# Potlačení PyTorch warnings
warnings.filterwarnings("ignore", category=UserWarning)
os.environ["PYTHONWARNINGS"] = "ignore"

# Nastavení pro Streamlit
os.environ["STREAMLIT_SERVER_ENABLE_STATIC_SERVING"] = "true"
os.environ["STREAMLIT_SERVER_ENABLE_CORS"] = "false"
os.environ["STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION"] = "false"

try:
    # Import a spuštění Streamlit
    import streamlit.web.cli as stcli
    import sys
    
    if __name__ == '__main__':
        sys.argv = ["streamlit", "run", "app.py", "--server.port=8502"]
        sys.exit(stcli.main())
        
except ImportError:
    print("Chyba: Streamlit není nainstalován.")
    print("Spusťte: pip install streamlit")
    sys.exit(1)
