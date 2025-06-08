**Výstup analýzy a přehled projektu MedDocAI Anonymizer**

**1. Celkový přehled a účel projektu:**

*   **Název projektu:** MedDocAI Anonymizer
*   **Účel:** Specializovaný nástroj pro anonymizaci osobních údajů ve zdravotnických dokumentech. Cílem je ochrana citlivých dat pacientů v souladu s nařízeními jako GDPR.
*   **Jazyková podpora:** Primárně čeština (včetně specifických entit jako rodná čísla, kódy diagnóz) a angličtina.
*   **Status (dle README.md):** PLNĚ FUNKČNÍ & MODULÁRNÍ, Produkčně připravená verze v2.0 (poslední aktualizace 7.6.2025).

**2. Architektura a technologie:**

*   **Hlavní komponenty:**
    *   **Streamlit UI:** Uživatelské rozhraní pro interaktivní anonymizaci (`app/main.py`).
    *   **FastAPI REST API:** Rozhraní pro programový přístup a dávkové zpracování (`api/main.py`).
    *   **Presidio Service:** Jádro anonymizační logiky, využívající Microsoft Presidio Analyzer a Anonymizer (`services/presidio_service.py`).
    *   **spaCy:** Pro základní NLP úlohy (tokenizace, detekce entit); využívá model `cs_core_news_sm` pro češtinu a `en_core_web_sm` pro angličtinu.
    *   **Vlastní rozpoznávače (Recognizers):** Moduly pro detekci českých specifických entit (viz bod 4).
*   **Kontejnerizace:** Projekt je plně kontejnerizovatelný pomocí Docker (`Dockerfile`, `docker-compose.yml`), což usnadňuje nasazení a škálovatelnost.
*   **Konfigurace:** Flexibilní konfigurační systém (`config/settings.py`) pro různá prostředí (development, production, testing).
*   **Logování:** Nastaveno pro různé úrovně a typy událostí (`config/logging_config.py`, ukládání do `logs/`).

**3. Struktura projektu (klíčové adresáře a soubory):**

*   `app/`: Kód pro Streamlit webovou aplikaci.
    *   `main.py`: Hlavní soubor Streamlit aplikace.
*   `api/`: Kód pro FastAPI REST API.
    *   `main.py`: Hlavní soubor FastAPI aplikace.
*   `services/`: Obsahuje klíčové služby.
    *   `presidio_service.py`: Integrace a využití Presidio.
    *   `batch_processor.py`: Logika pro dávkové zpracování souborů.
*   `recognizers/`: Implementace vlastních rozpoznávačů entit.
    *   `birth_number.py`, `diagnosis_codes.py`, `health_insurance.py`, `medical_facilities.py`, `addresses.py`: Rozpoznávače pro specifické české entity.
    *   `registry.py`: Registrace vlastních rozpoznávačů do Presidia.
*   `models/`: Datové modely (např. `document.py`).
*   `config/`: Konfigurační soubory.
*   `czech_model/`: Stáhnutý spaCy model pro češtinu.
*   `tests/`: Automatizované testy (jednotkové, integrační).
*   `PRD/`: Produktová dokumentace (instalační manuál, uživatelský manuál atd.).
*   `Dockerfile`, `docker-compose.yml`: Konfigurace pro Docker.
*   `requirements.txt`: Seznam Python závislostí.
*   `README.md`: Hlavní dokumentační soubor s přehledem projektu.

**4. Rozpoznávané entity:**

*   **Standardní (Presidio):** PERSON, EMAIL_ADDRESS, PHONE_NUMBER, LOCATION, DATE_TIME, US_SSN atd.
*   **České specializované:**
    *   `CZECH_BIRTH_NUMBER` (Rodné číslo)
    *   `CZECH_MEDICAL_FACILITY` (Zdravotnická zařízení)
    *   `CZECH_DIAGNOSIS_CODE` (Kódy diagnóz MKN-10)
    *   `CZECH_ADDRESS` (České adresy)
    *   `CZECH_HEALTH_INSURANCE_NUMBER` (Číslo zdravotního pojištěnce – často podobné RČ)

**5. Funkcionalita:**

*   **Anonymizace textu:** Přímé vložení textu do UI nebo přes API.
*   **Anonymizace souborů:** Nahrání souborů (podporované typy definovány v konfiguraci, např. .txt, .docx) přes API.
*   **Dávkové zpracování:** Možnost anonymizovat více souborů najednou přes API.
*   **Metody anonymizace:** Nahrazení (`replace`), maskování (`mask`), redakce (`redact`) – konfigurovatelné.
*   **Nastavení prahu spolehlivosti (Confidence Threshold):** Umožňuje uživateli určit minimální skóre spolehlivosti pro rozpoznání entity.

**6. Instalace a spuštění:**

*   **Požadavky:** Python 3.11+, spaCy model, Docker (volitelně).
*   **Instalace:** Klonování repozitáře, vytvoření virtuálního prostředí, instalace závislostí (`pip install -r requirements.txt`), stažení spaCy modelu.
*   **Spuštění:**
    *   Webová aplikace: `python run_app.py` nebo `make app` nebo `streamlit run app/main.py`.
    *   REST API: `python run_api.py` nebo `make api`.
    *   Docker: `make docker-build` & `make docker-run` nebo `make docker-compose-up`.

**7. Testování:**

*   Projekt obsahuje sadu testů ve složce `tests/` (např. `test_presidio_service.py`, `test_czech_recognizers.py`).
*   Testy se spouští pomocí `pytest`.

**8. Vývojová fáze a možná budoucí roadmapa:**

*   **Aktuální fáze:** Produkčně připravená verze 2.0. Systém je stabilní a funkční.
*   **Roadmapa:** Podrobná roadmapa projektu je definována v samostatném dokumentu [ROADMAP.md](docs/ROADMAP.md). Klíčové možné budoucí směry zahrnují:
    *   Údržba, opravy chyb.
    *   Optimalizace výkonu a správy zdrojů.
    *   Přidání nových rozpoznávačů pro další typy citlivých dat nebo pro jiné jazyky.
    *   Vylepšení stávajících rozpoznávačů (zvýšení přesnosti, pokrytí více variant).
    *   Rozšíření funkcionality API nebo webové aplikace.
    *   Pravidelné bezpečnostní audity a aktualizace.

**9. Závěr analýzy:**

MedDocAI Anonymizer je dobře strukturovaný a komplexní projekt, který řeší specifickou potřebu anonymizace citlivých dat ve zdravotnictví s důrazem na české prostředí. Využívá moderní technologie a postupy (Presidio, spaCy, FastAPI, Streamlit, Docker). Projekt je ve zralé fázi vývoje s dobrou úrovní dokumentace a testování.
