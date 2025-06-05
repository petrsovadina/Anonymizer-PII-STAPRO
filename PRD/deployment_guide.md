# Průvodce lokálním nasazením MedDocAI Anonymizer

## Přehled
Tento průvodce vás provede kroky pro lokální nasazení MedDocAI Anonymizer na vašem systému.

## Systémové požadavky

### Minimální požadavky
- **OS**: Windows 10/11, macOS 10.15+, Ubuntu 18.04+
- **Python**: 3.8 nebo novější
- **RAM**: 4 GB (doporučeno 8 GB)
- **Disk**: 2 GB volného místa
- **Internet**: Pro stažení závislostí

### Doporučené požadavky
- **RAM**: 8-16 GB
- **CPU**: 4+ jádra
- **Disk**: SSD disk pro lepší výkon

## Rychlá instalace

### 1. Automatická instalace (doporučeno)
```bash
# Stažení a spuštění instalačního skriptu
python setup_deployment.py
```

Tento skript automaticky:
- Zkontroluje systémové požadavky
- Vytvoří virtuální prostředí
- Nainstaluje všechny závislosti
- Nastaví spaCy modely (včetně českého)
- Vytvoří potřebné adresáře
- Nakonfiguruje aplikaci
- Vytvoří spouštěcí skripty

### 2. Spuštění aplikace

#### Linux/macOS:
```bash
./start.sh
```

#### Windows:
```batch
start.bat
```

### 3. Přístup k aplikaci
- **Streamlit UI**: http://localhost:8501
- **API dokumentace**: http://localhost:8000/docs
- **API endpoint**: http://localhost:8000

### 4. Zastavení aplikace

#### Linux/macOS:
```bash
./stop.sh
```

#### Windows:
```batch
stop.bat
```

## Manuální instalace

Pokud automatická instalace nefunguje, postupujte manuálně:

### Krok 1: Příprava prostředí
```bash
# Vytvoření virtuálního prostředí
python -m venv venv

# Aktivace (Linux/macOS)
source venv/bin/activate

# Aktivace (Windows)
venv\Scripts\activate

# Aktualizace pip
pip install --upgrade pip
```

### Krok 2: Instalace závislostí
```bash
# Instalace Python balíčků
pip install -r requirements.txt

# Stažení anglického spaCy modelu
python -m spacy download en_core_web_sm

# Vytvoření českého modelu
python setup_czech_spacy.py
```

### Krok 3: Konfigurace
```bash
# Vytvoření konfiguračního souboru
cp .env.example .env

# Úprava konfigurace (volitelně)
nano .env
```

### Krok 4: Spuštění služeb
```bash
# Streamlit aplikace (v jednom terminálu)
streamlit run run_streamlit.py --server.port 8501

# FastAPI server (v druhém terminálu)
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## Struktura projektu po instalaci

```
Anonymizer-PII-STAPRO/
├── 📁 venv/                    # Virtuální prostředí
├── 📁 czech_model/            # Český spaCy model
├── 📁 logs/                   # Log soubory
├── 📁 uploads/                # Nahrané soubory
├── 📁 exports/                # Exportované výsledky
├── 📁 temp/                   # Dočasné soubory
├── 📁 PRD/                    # Dokumentace
├── 🔧 .env                    # Konfigurace
├── 🚀 start.sh / start.bat    # Spouštěcí skripty
├── 🛑 stop.sh / stop.bat      # Zastavovací skripty
├── 📋 requirements.txt        # Python závislosti
├── 🏗️ setup_deployment.py     # Instalační skript
├── 🔧 setup_czech_spacy.py    # Skript pro český model
└── 📱 run_streamlit.py        # Streamlit aplikace
```

## Konfigurace (.env soubor)

```env
# Server nastavení
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Presidio nastavení
SCORE_THRESHOLD=0.3
DEFAULT_LANGUAGE=cs

# Bezpečnost
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=["http://localhost:8501"]

# Limity
MAX_FILE_SIZE=50MB
MAX_BATCH_SIZE=100
```

## Testování instalace

### Test základní funkčnosti
```bash
# Test spaCy modelů
python test_models.py

# Test anonymizace
python test_anonymize.py

# Test API
curl http://localhost:8000/health
```

### Test přes webové rozhraní
1. Otevřete http://localhost:8501
2. Nahrajte testovací dokument
3. Spusťte anonymizaci
4. Zkontrolujte výsledky

## Řešení problémů

### Časté problémy

#### 1. Python není nainstalován
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install python3 python3-pip python3-venv

# macOS (s Homebrew)
brew install python

# Windows: Stáhněte z python.org
```

#### 2. Chyba při instalaci spaCy
```bash
# Alternativní instalace
pip install spacy --upgrade
python -m spacy download en_core_web_sm --upgrade
```

#### 3. Problémy s porty
```bash
# Kontrola používaných portů
netstat -tulpn | grep :8000
netstat -tulpn | grep :8501

# Zastavení procesů
pkill -f streamlit
pkill -f uvicorn
```

#### 4. Nedostatek paměti
- Snižte batch size v konfiguraci
- Zavřete ostatní aplikace
- Zvyšte virtuální paměť

#### 5. Český model nefunguje
```bash
# Opětovné vytvoření českého modelu
rm -rf czech_model
python setup_czech_spacy.py
```

### Logs a diagnostika
```bash
# Prohlížení logů
tail -f logs/application.log

# Kontrola stavu služeb
ps aux | grep streamlit
ps aux | grep uvicorn
```

## Aktualizace aplikace

### Aktualizace kódu
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

### Aktualizace modelů
```bash
python -m spacy download en_core_web_sm --upgrade
python setup_czech_spacy.py
```

## Produkční nasazení

Pro produkční nasazení doporučujeme:

### 1. Bezpečnost
- Změňte SECRET_KEY v .env
- Nastavte DEBUG=False
- Používejte HTTPS
- Omezte ALLOWED_ORIGINS

### 2. Výkon
- Použijte více workers: `--workers 4`
- Nastavte cache pro modely
- Použijte load balancer

### 3. Monitoring
- Nastavte centralizované logování
- Implementujte health checks
- Monitorujte využití zdrojů

### 4. Backup
- Zálohujte konfiguraci
- Zálohujte zpracované dokumenty
- Zálohujte vlastní modely

## Podpora

### Kontakty
- **Dokumentace**: `/PRD/` adresář
- **Issues**: GitHub repository
- **Email**: [kontakt]

### Další zdroje
- [Presidio dokumentace](https://microsoft.github.io/presidio/)
- [spaCy dokumentace](https://spacy.io/)
- [Streamlit dokumentace](https://docs.streamlit.io/)
- [FastAPI dokumentace](https://fastapi.tiangolo.com/)
