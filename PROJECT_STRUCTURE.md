# MedDocAI Anonymizer - Struktura projektu

## 📁 Aktuální struktura (6.6.2025)

### 🎯 Hlavní aplikace
- `app.py` - **Streamlit webové rozhraní** (hlavní aplikace)
- `presidio_service.py` - **Anonymizační služba** (Microsoft Presidio)
- `run_app.py` - **Alternativní spouštěč** (bez PyTorch warnings)

### 🇨🇿 České rozpoznávače
- `czech_registry.py` - **Registr českých rozpoznávačů**
- `czech_birth_number_recognizer.py` - **Rodná čísla**
- `czech_address_recognizer.py` - **České adresy**
- `czech_health_insurance_recognizer.py` - **Zdravotní pojišťovny**
- `czech_diagnosis_code_recognizer.py` - **Kódy diagnóz**
- `czech_medical_facility_recognizer.py` - **Zdravotnická zařízení**

### 🔧 Anonymizační operátory
- `czech_birth_number_operator.py` - **Operátor pro rodná čísla**
- `czech_address_operator.py` - **Operátor pro adresy**
- `czech_medical_diagnosis_operator.py` - **Operátor pro diagnózy**
- `czech_medical_facility_operator.py` - **Operátor pro zařízení**

### 📄 Dokumenty a modely
- `document.py` - **Datové modely** (Document, AnonymizedDocument)
- `batch_processor.py` - **Dávkové zpracování**

### 🧪 Testování
- `test_models.py` - **Test základních modelů**
- `test_anonymize.py` - **Test anonymizace**

### 📚 Dokumentace
- `README.md` - **Hlavní dokumentace**
- `PYTORCH_FIX_README.md` - **Technické řešení PyTorch**
- `FINAL_VERIFICATION_CHECKLIST.md` - **Kontrolní seznam**
- `PROJECT_STRUCTURE.md` - **Tento soubor**

### ⚙️ Konfigurace
- `requirements.txt` - **Python závislosti**
- `.env` - **Konfigurační soubor**
- `__init__.py` - **Python balíček**

### 📂 Adresáře
- `czech_model/` - **České spaCy modely**
- `PRD/` - **Rozšířená dokumentace**
- `logs/` - **Log soubory**
- `uploads/` - **Nahrané soubory**
- `exports/` - **Exportované výsledky**

## 🗑️ Odstraněné zastaralé soubory

### Duplikátní dokumentace:
- ❌ `FINAL_DEPLOYMENT_STATUS.md`
- ❌ `DEPLOYMENT_SUMMARY.md`
- ❌ `czech_spacy_solution.md`

### Nepoužívané aplikace:
- ❌ `main.py`
- ❌ `simple_app.py`
- ❌ `run_streamlit.py`

### Zastaralé nástroje:
- ❌ `setup_deployment.py`
- ❌ `setup_czech_spacy.py`
- ❌ `parallel_batch_processor.py`
- ❌ `stress_test.py`
- ❌ `test_batch_processing.py`
- ❌ `test_streamlit_app.py`

### Nepoužívané skripty:
- ❌ `start.sh / start.bat`
- ❌ `stop.sh / stop.bat`

## 🚀 Spuštění aplikace

**Hlavní způsob:**
```bash
streamlit run app.py
```

**Alternativní způsob:**
```bash
python run_app.py
```

## 📋 Dependency flow

```
app.py
├── presidio_service.py
│   ├── czech_registry.py
│   │   ├── czech_birth_number_recognizer.py
│   │   ├── czech_address_recognizer.py
│   │   ├── czech_health_insurance_recognizer.py
│   │   ├── czech_diagnosis_code_recognizer.py
│   │   └── czech_medical_facility_recognizer.py
│   └── document.py
└── batch_processor.py (volitelné)
```

## ✅ Status: ČISTÉ A FUNKČNÍ

Projekt nyní obsahuje pouze relevantní soubory bez duplicit a zastaralého kódu.
