# Architektura MedDocAI Anonymizer

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

## 🧪 Testování
```bash
python -m pytest tests/
```

## 📁 Organizace modulů

### app/
Obsahuje hlavní Streamlit aplikaci a uživatelské rozhraní.

### services/
Jádro aplikace - služby pro anonymizaci a dávkové zpracování.

### recognizers/
České rozpoznávače pro specifické typy dat ve zdravotnictví.

### operators/
Operátory definující způsoby anonymizace různých typů entit.

### models/
Datové modely použité napříč aplikací.

### tests/
Kompletní testovací sada - unit, integrační testy a fixtures.
