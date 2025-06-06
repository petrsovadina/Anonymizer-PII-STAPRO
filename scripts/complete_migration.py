#!/usr/bin/env python3
"""
Migračný skript pro dokončení reorganizace MedDocAI Anonymizer.
Tento skript dokončí přesun souborů a vyčistí starý kód.
"""

import os
import shutil
from pathlib import Path

def cleanup_old_files():
    """Vyčistí staré soubory v root directory."""
    
    root_dir = Path(__file__).parent.parent
    
    # Soubory k vymazání (starý app.py zůstane jako backup)
    files_to_move_or_delete = [
        # Tyto soubory jsou již přesunuté do správných složek
    ]
    
    print("🧹 Čistění starých souborů...")
    
    # Přejmenujeme starý app.py jako backup
    old_app = root_dir / "app.py"
    if old_app.exists():
        backup_app = root_dir / "app_backup.py"
        if not backup_app.exists():
            shutil.move(str(old_app), str(backup_app))
            print(f"✅ Přejmenován app.py na app_backup.py")
    
    print("✅ Čistění dokončeno!")

def verify_structure():
    """Ověří, že nová struktura je kompletní."""
    
    root_dir = Path(__file__).parent.parent
    
    required_dirs = [
        "app",
        "services", 
        "recognizers",
        "operators",
        "models",
        "tests",
        "docs",
        "scripts",
        "config"
    ]
    
    required_files = [
        "app/main.py",
        "services/presidio_service.py",
        "services/batch_processor.py",
        "recognizers/registry.py",
        "models/document.py",
        "run_app.py",
        "requirements.txt"
    ]
    
    print("🔍 Ověřování struktury...")
    
    # Kontrola adresářů
    for directory in required_dirs:
        dir_path = root_dir / directory
        if dir_path.exists():
            print(f"✅ Adresář {directory} existuje")
        else:
            print(f"❌ Chybí adresář {directory}")
    
    # Kontrola souborů
    for file in required_files:
        file_path = root_dir / file
        if file_path.exists():
            print(f"✅ Soubor {file} existuje")
        else:
            print(f"❌ Chybí soubor {file}")
    
    print("✅ Ověření dokončeno!")

def create_architecture_docs():
    """Vytvoří dokumentaci architektury."""
    
    root_dir = Path(__file__).parent.parent
    docs_dir = root_dir / "docs"
    
    architecture_content = """# Architektura MedDocAI Anonymizer

## 📋 Přehled
MedDocAI Anonymizer je modulární aplikace pro anonymizaci osobních údajů v zdravotnických dokumentech.

## 🏗️ Struktura projektu

```
MedDocAI-Anonymizer/
├── 📱 app/                    # Hlavní aplikace
│   ├── main.py               # Streamlit UI
│   └── __init__.py
│
├── 🔧 services/              # Služby a jádro systému
│   ├── presidio_service.py   # Hlavní anonymizační služba
│   ├── batch_processor.py    # Dávkové zpracování
│   └── __init__.py
│
├── 🇨🇿 recognizers/          # České rozpoznávače
│   ├── registry.py           # Registr rozpoznávačů
│   ├── birth_number.py       # Rodná čísla
│   ├── health_insurance.py   # Zdravotní pojištění
│   ├── diagnosis_codes.py    # Kódy diagnóz
│   ├── medical_facilities.py # Zdravotnická zařízení
│   ├── addresses.py          # České adresy
│   └── __init__.py
│
├── 🛠️ operators/             # Anonymizační operátory
│   ├── czech_*_operator.py  # Specializované operátory
│   └── __init__.py
│
├── 📊 models/                # Datové modely
│   ├── document.py           # Dokumentové modely
│   └── __init__.py
│
├── 🧪 tests/                 # Testování
│   ├── unit/                 # Unit testy
│   ├── integration/          # Integrační testy
│   ├── fixtures/             # Testovací data
│   └── __init__.py
│
├── 📚 docs/                  # Dokumentace
├── 🔧 scripts/               # Pomocné skripty
└── ⚙️ config/                # Konfigurace
```

## 🔄 Tok dat

1. **Vstup**: Uživatel zadá text v Streamlit rozhraní
2. **Zpracování**: PresidioService analyzuje text pomocí českých rozpoznávačů
3. **Anonymizace**: Detekované entity jsou anonymizovány pomocí operátorů
4. **Výstup**: Anonymizovaný text je zobrazen uživateli

## 🎯 Rozpoznávané entity

### Standardní (Presidio):
- PERSON, EMAIL_ADDRESS, PHONE_NUMBER, LOCATION, DATE_TIME

### České specializované:
- CZECH_BIRTH_NUMBER, CZECH_MEDICAL_FACILITY, CZECH_DIAGNOSIS_CODE, CZECH_ADDRESS

## 🚀 Spuštění
```bash
python run_app.py
```
"""
    
    arch_file = docs_dir / "architecture.md"
    with open(arch_file, "w", encoding="utf-8") as f:
        f.write(architecture_content)
    
    print(f"✅ Vytvořena dokumentace architektury: {arch_file}")

def main():
    """Hlavní funkce migrace."""
    
    print("🚀 Spouštím dokončení reorganizace MedDocAI Anonymizer...")
    
    # 1. Vyčistění starých souborů
    cleanup_old_files()
    
    # 2. Ověření struktury
    verify_structure()
    
    # 3. Vytvoření dokumentace
    create_architecture_docs()
    
    print("\n🎉 Reorganizace dokončena!")
    print("\n📋 Další kroky:")
    print("1. Spusťte testy: python -m pytest tests/")
    print("2. Spusťte aplikaci: python run_app.py")
    print("3. Zkontrolujte dokumentaci v docs/")

if __name__ == "__main__":
    main()
