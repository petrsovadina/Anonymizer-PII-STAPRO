# Instrukce pro vývojáře MedDocAI Anonymizer

## Obsah
1. [Úvod](#úvod)
2. [Vývojové prostředí](#vývojové-prostředí)
   - [Požadavky](#požadavky)
   - [Nastavení prostředí](#nastavení-prostředí)
   - [Struktura projektu](#struktura-projektu)
3. [Workflow vývoje](#workflow-vývoje)
   - [Git workflow](#git-workflow)
   - [Code review proces](#code-review-proces)
   - [CI/CD pipeline](#cicd-pipeline)
4. [Coding standards](#coding-standards)
   - [Python style guide](#python-style-guide)
   - [Dokumentace kódu](#dokumentace-kódu)
   - [Logování](#logování)
   - [Zpracování chyb](#zpracování-chyb)
5. [Best practices](#best-practices)
   - [Bezpečnost](#bezpečnost)
   - [Výkon](#výkon)
   - [Testování](#testování)
   - [Práce s NLP modely](#práce-s-nlp-modely)
6. [Implementační detaily](#implementační-detaily)
   - [Rozšíření Presidio](#rozšíření-presidio)
   - [Vlastní rozpoznávače](#vlastní-rozpoznávače)
   - [Vlastní anonymizační operátory](#vlastní-anonymizační-operátory)
   - [Integrace NLP modelů](#integrace-nlp-modelů)
7. [Deployment](#deployment)
   - [Lokální deployment](#lokální-deployment)
   - [Staging deployment](#staging-deployment)
   - [Produkční deployment](#produkční-deployment)
8. [Troubleshooting](#troubleshooting)
   - [Známé problémy](#známé-problémy)
   - [Debugging](#debugging)
   - [Podpora](#podpora)

## Úvod

Tento dokument poskytuje praktické instrukce pro vývojáře pracující na projektu MedDocAI Anonymizer. Obsahuje informace o vývojovém prostředí, workflow, coding standards, best practices a implementačních detailech.

Před zahájením práce se důkladně seznamte s následujícími dokumenty:
- Produktová specifikace
- Vývojový plán a harmonogram
- Technická dokumentace

## Vývojové prostředí

### Požadavky

- **Python**: 3.11+ (doporučeno 3.11)
- **Docker**: 24.0+
- **Docker Compose**: 2.20+
- **Git**: 2.40+
- **IDE**: PyCharm, VS Code nebo jiné s podporou Python
- **Kubernetes**: minikube nebo kind pro lokální vývoj (volitelné)

### Nastavení prostředí

1. **Klonování repozitáře**:
   ```bash
   git clone https://gitlab.stapro.cz/ai/meddocai-anonymizer.git
   cd meddocai-anonymizer
   ```

2. **Vytvoření virtuálního prostředí**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. **Instalace závislostí**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Vývojářské nástroje
   ```

4. **Nastavení pre-commit hooks**:
   ```bash
   pre-commit install
   ```

5. **Spuštění lokálního vývojového prostředí**:
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

6. **Ověření nastavení**:
   ```bash
   pytest tests/smoke
   ```

### Struktura projektu

```
meddocai-anonymizer/
├── .github/                  # GitHub workflow konfigurace
├── .gitlab/                  # GitLab CI/CD konfigurace
├── docs/                     # Dokumentace
├── kubernetes/               # Kubernetes manifesty
├── scripts/                  # Pomocné skripty
├── src/                      # Zdrojový kód
│   ├── api/                  # API Gateway
│   ├── preprocessing/        # Služba předzpracování
│   ├── detection/            # Služba detekce PII
│   │   ├── recognizers/      # Vlastní rozpoznávače
│   │   └── models/           # NLP modely
│   ├── anonymization/        # Služba anonymizace
│   │   └── operators/        # Vlastní anonymizační operátory
│   ├── validation/           # Služba validace
│   ├── batch/                # Dávkový zpracovatel
│   ├── config/               # Služba konfigurace
│   ├── common/               # Sdílené komponenty
│   │   ├── models/           # Datové modely
│   │   ├── utils/            # Utility
│   │   └── logging/          # Logování
│   └── main.py               # Vstupní bod aplikace
├── tests/                    # Testy
│   ├── unit/                 # Unit testy
│   ├── integration/          # Integrační testy
│   ├── api/                  # API testy
│   ├── e2e/                  # End-to-end testy
│   └── smoke/                # Smoke testy
├── .env.example              # Vzorový konfigurační soubor
├── .gitignore                # Git ignore soubor
├── .pre-commit-config.yaml   # Pre-commit konfigurace
├── docker-compose.yml        # Docker Compose pro produkci
├── docker-compose.dev.yml    # Docker Compose pro vývoj
├── Dockerfile                # Dockerfile pro produkci
├── Dockerfile.dev            # Dockerfile pro vývoj
├── pyproject.toml            # Python projekt konfigurace
├── README.md                 # Readme soubor
└── requirements.txt          # Závislosti
```

## Workflow vývoje

### Git workflow

Používáme **GitFlow** workflow s následujícími větvemi:

- **main**: Produkční kód, vždy stabilní
- **develop**: Vývojová větev, integrační bod pro feature větve
- **feature/\***: Nové funkce (např. `feature/czech-recognizers`)
- **bugfix/\***: Opravy chyb (např. `bugfix/api-validation`)
- **release/\***: Příprava vydání (např. `release/1.0.0`)
- **hotfix/\***: Kritické opravy v produkci (např. `hotfix/security-fix`)

**Postup pro vývoj nové funkce**:

1. Vytvořte novou feature větev z develop:
   ```bash
   git checkout develop
   git pull
   git checkout -b feature/nazev-funkce
   ```

2. Implementujte funkci a commitujte změny:
   ```bash
   git add .
   git commit -m "Popis změn"
   ```

3. Pravidelně synchronizujte s develop větví:
   ```bash
   git checkout develop
   git pull
   git checkout feature/nazev-funkce
   git merge develop
   ```

4. Po dokončení vytvořte Merge Request (MR) do develop větve.

### Code review proces

1. **Vytvoření MR**:
   - Vyplňte šablonu MR s popisem změn, testovacími postupy a případnými poznámkami.
   - Přiřaďte MR k příslušnému issue.
   - Přidejte štítky (labels) pro snadnější kategorizaci.

2. **Kontrola CI/CD**:
   - Ujistěte se, že všechny automatizované testy a kontroly prošly úspěšně.
   - Opravte případné chyby před žádostí o review.

3. **Code review**:
   - Přiřaďte alespoň dva reviewery.
   - Reagujte na komentáře a provádějte požadované změny.
   - Po schválení všemi reviewery může být MR sloučen.

4. **Sloučení (merge)**:
   - Používejte "Squash and merge" pro udržení čisté historie.
   - Ujistěte se, že commit message je popisná a následuje konvence.

### CI/CD pipeline

Naše CI/CD pipeline zahrnuje následující kroky:

1. **Build**: Sestavení Docker image.
2. **Lint**: Kontrola kódu pomocí flake8, black, isort.
3. **Test**: Spuštění unit a integračních testů.
4. **Security Scan**: Kontrola bezpečnostních zranitelností.
5. **Deploy to Dev**: Automatické nasazení do vývojového prostředí.
6. **Deploy to Staging**: Manuální spuštění nasazení do staging prostředí.
7. **Deploy to Production**: Manuální spuštění nasazení do produkčního prostředí.

## Coding standards

### Python style guide

Dodržujeme [PEP 8](https://www.python.org/dev/peps/pep-0008/) s následujícími upřesněními:

- **Formátování**: Používáme [Black](https://black.readthedocs.io/) s výchozí konfigurací.
- **Import sorting**: Používáme [isort](https://pycqa.github.io/isort/) s konfigurací kompatibilní s Black.
- **Linting**: Používáme [flake8](https://flake8.pycqa.org/) s rozšířeními.
- **Type hints**: Používáme typové anotace pro všechny funkce a metody.

**Příklad**:

```python
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from presidio_analyzer import PatternRecognizer

from meddocai.common.models import Document
from meddocai.common.utils import normalize_text


def process_document(
    document: Document, config: Dict[str, any] = None
) -> Optional[Document]:
    """
    Process a document using the specified configuration.

    Args:
        document: The document to process.
        config: Optional configuration dictionary.

    Returns:
        Processed document or None if processing failed.
    """
    if not document or not document.content:
        return None

    normalized_text = normalize_text(document.content)
    
    # Processing logic here
    
    return document
```

### Dokumentace kódu

- **Docstrings**: Používáme [Google style docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html).
- **Moduly**: Každý modul musí mít docstring popisující jeho účel.
- **Třídy a funkce**: Všechny veřejné třídy a funkce musí mít docstring.
- **Komplexní logika**: Složité části kódu musí být okomentovány.

### Logování

Používáme standardní Python `logging` modul s následujícími úrovněmi:

- **DEBUG**: Detailní informace pro debugging.
- **INFO**: Potvrzení, že věci fungují podle očekávání.
- **WARNING**: Indikace potenciálních problémů.
- **ERROR**: Chyby, které znemožňují funkci.
- **CRITICAL**: Kritické chyby vyžadující okamžitou pozornost.

**Příklad**:

```python
import logging

logger = logging.getLogger(__name__)

def process_batch(batch_id: str, documents: List[Document]) -> bool:
    logger.info(f"Starting processing batch {batch_id} with {len(documents)} documents")
    
    try:
        # Processing logic
        logger.debug(f"Batch {batch_id} processing details: ...")
        return True
    except Exception as e:
        logger.error(f"Error processing batch {batch_id}: {str(e)}", exc_info=True)
        return False
```

### Zpracování chyb

- **Specifické výjimky**: Vytvářejte a používejte specifické výjimky pro různé typy chyb.
- **Zachytávání výjimek**: Zachytávejte pouze specifické výjimky, ne obecné `Exception` (pokud to není nezbytné).
- **Logování**: Vždy logujte výjimky s kontextem a stack trace.
- **Graceful degradation**: Navrhujte systém tak, aby se zotavil z chyb, když je to možné.

**Příklad**:

```python
class DocumentProcessingError(Exception):
    """Raised when document processing fails."""
    pass

class InvalidDocumentError(DocumentProcessingError):
    """Raised when document is invalid."""
    pass

def validate_document(document: Document) -> None:
    if not document:
        raise InvalidDocumentError("Document is None")
    
    if not document.content:
        raise InvalidDocumentError("Document has no content")
    
    # More validation...
```

## Best practices

### Bezpečnost

- **Secrets management**: Nikdy neukládejte citlivé informace (hesla, API klíče) do kódu nebo verzovacího systému.
- **Input validation**: Vždy validujte vstupy, zejména ty z externích zdrojů.
- **OWASP Top 10**: Buďte obeznámeni s [OWASP Top 10](https://owasp.org/www-project-top-ten/) a implementujte příslušná opatření.
- **Dependency scanning**: Pravidelně kontrolujte závislosti na známé zranitelnosti.

### Výkon

- **Profilování**: Používejte nástroje jako `cProfile` nebo `py-spy` pro identifikaci úzkých míst.
- **Lazy loading**: Načítejte velké objekty nebo modely pouze když jsou potřeba.
- **Caching**: Implementujte caching pro často používané operace nebo data.
- **Asynchronní zpracování**: Používejte asynchronní zpracování pro I/O vázané operace.

### Testování

- **Test-driven development (TDD)**: Pište testy před implementací funkce.
- **Unit testy**: Každá funkce nebo metoda by měla mít unit testy.
- **Integrační testy**: Testujte interakce mezi komponentami.
- **Mocking**: Používejte `unittest.mock` nebo `pytest-mock` pro izolaci testovaného kódu.
- **Fixtures**: Používejte pytest fixtures pro sdílení testovacích dat a setup/teardown.

**Příklad unit testu**:

```python
import pytest
from unittest.mock import MagicMock, patch

from meddocai.detection.recognizers import CzechBirthNumberRecognizer

@pytest.fixture
def recognizer():
    return CzechBirthNumberRecognizer()

def test_recognize_valid_birth_number(recognizer):
    # Given
    text = "Pacient: Jan Novák, r.č. 760123/1234"
    
    # When
    results = recognizer.analyze(text, ["CZECH_BIRTH_NUMBER"])
    
    # Then
    assert len(results) == 1
    assert results[0].entity_type == "CZECH_BIRTH_NUMBER"
    assert results[0].start == 24
    assert results[0].end == 36
    assert results[0].score > 0.8

@patch("meddocai.detection.recognizers.validate_czech_birth_number")
def test_validation_called(mock_validate, recognizer):
    # Given
    text = "r.č. 760123/1234"
    mock_validate.return_value = True
    
    # When
    recognizer.analyze(text, ["CZECH_BIRTH_NUMBER"])
    
    # Then
    mock_validate.assert_called_once_with("760123/1234")
```

### Práce s NLP modely

- **Model versioning**: Verzujte modely a jejich konfiguraci.
- **Evaluation**: Pravidelně vyhodnocujte výkon modelů na testovacích datech.
- **Optimalizace**: Používejte techniky jako kvantizace pro optimalizaci velikosti a rychlosti modelů.
- **Caching**: Cachujte výsledky inference pro často používané vstupy.

## Implementační detaily

### Rozšíření Presidio

Microsoft Presidio poskytuje framework pro detekci a anonymizaci PII, který budeme rozšiřovat pro české zdravotnické prostředí.

**Klíčové komponenty Presidio**:

1. **Presidio Analyzer**: Detekce PII entit v textu.
2. **Presidio Anonymizer**: Anonymizace detekovaných entit.
3. **Presidio Image Redactor**: Redakce textu v obrázcích.

### Vlastní rozpoznávače

Pro implementaci vlastního rozpoznávače je potřeba vytvořit třídu, která dědí z `EntityRecognizer` nebo `PatternRecognizer`.

**Příklad implementace rozpoznávače rodných čísel**:

```python
from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer
from presidio_analyzer.nlp_engine import NlpArtifacts

class CzechBirthNumberRecognizer(PatternRecognizer):
    """
    Recognizer for Czech birth numbers (rodná čísla).
    
    Formats:
    - YYMMDD/XXXX (with slash)
    - YYMMDDXXXX (without slash)
    """
    
    def __init__(self):
        patterns = [
            Pattern(
                name="czech_birth_number_with_slash",
                regex=r"\b(\d{6})\/(\d{3,4})\b",
                score=0.9
            ),
            Pattern(
                name="czech_birth_number_without_slash",
                regex=r"\b\d{9,10}\b",
                score=0.7
            )
        ]
        
        context = ["rodné", "číslo", "r.č.", "rč", "narozen"]
        
        super().__init__(
            supported_entity="CZECH_BIRTH_NUMBER",
            patterns=patterns,
            context=context,
            name="CzechBirthNumberRecognizer"
        )
    
    def validate_result(self, pattern_text: str) -> bool:
        """
        Validate if the pattern is a valid Czech birth number.
        
        Args:
            pattern_text: The text to validate.
            
        Returns:
            True if the text is a valid Czech birth number, False otherwise.
        """
        # Remove slash if present
        clean_text = pattern_text.replace("/", "")
        
        # Basic validation
        if not clean_text.isdigit():
            return False
        
        if len(clean_text) not in [9, 10]:
            return False
        
        # Extract components
        year = int(clean_text[0:2])
        month = int(clean_text[2:4])
        day = int(clean_text[4:6])
        
        # Validate date components
        if month > 50:
            month -= 50  # Female birth numbers have month + 50
        
        if not (1 <= month <= 12):
            return False
        
        if not (1 <= day <= 31):
            return False
        
        # Validate checksum for 10-digit numbers
        if len(clean_text) == 10:
            number = int(clean_text)
            return number % 11 == 0
        
        return True
```

### Vlastní anonymizační operátory

Pro implementaci vlastního anonymizačního operátoru je potřeba vytvořit třídu, která dědí z `Operator`.

**Příklad implementace operátoru pro syntetická česká jména**:

```python
import random
from typing import Dict, Optional

from presidio_anonymizer.entities import OperatorConfig
from presidio_anonymizer.operators import Operator

class CzechNameOperator(Operator):
    """
    Operator that replaces names with synthetic Czech names.
    """
    
    def __init__(self):
        super().__init__()
        # Load name lists
        self.male_first_names = ["Jan", "Petr", "Josef", "Pavel", "Martin", "Tomáš", "Jiří", "Miroslav", "Zdeněk", "Václav"]
        self.female_first_names = ["Jana", "Eva", "Hana", "Marie", "Anna", "Lenka", "Kateřina", "Lucie", "Věra", "Alena"]
        self.last_names_male = ["Novák", "Svoboda", "Novotný", "Dvořák", "Černý", "Procházka", "Kučera", "Veselý", "Horák", "Němec"]
        self.last_names_female = ["Nováková", "Svobodová", "Novotná", "Dvořáková", "Černá", "Procházková", "Kučerová", "Veselá", "Horáková", "Němcová"]
    
    def operate(self, text: Optional[str] = None, params: Optional[Dict] = None) -> str:
        """
        Replace the text with a synthetic Czech name.
        
        Args:
            text: The original text to be replaced.
            params: Additional parameters (gender, full_name).
            
        Returns:
            A synthetic Czech name.
        """
        if not text:
            return ""
        
        params = params or {}
        gender = params.get("gender", self._detect_gender(text))
        full_name = params.get("full_name", " " in text)
        
        if gender == "female":
            first_name = random.choice(self.female_first_names)
            last_name = random.choice(self.last_names_female)
        else:
            first_name = random.choice(self.male_first_names)
            last_name = random.choice(self.last_names_male)
        
        if full_name:
            return f"{first_name} {last_name}"
        elif self._is_likely_first_name(text):
            return first_name
        else:
            return last_name
    
    def _detect_gender(self, text: str) -> str:
        """
        Detect gender based on the text.
        
        Args:
            text: The text to analyze.
            
        Returns:
            "female" if likely female, "male" otherwise.
        """
        # Simple heuristic: check for female surname endings
        return "female" if "ová" in text else "male"
    
    def _is_likely_first_name(self, text: str) -> bool:
        """
        Determine if the text is likely a first name.
        
        Args:
            text: The text to analyze.
            
        Returns:
            True if likely a first name, False otherwise.
        """
        # Simple heuristic based on length
        return len(text) <= 6
    
    def validate(self, params: Optional[Dict] = None) -> bool:
        """
        Validate the parameters.
        
        Args:
            params: The parameters to validate.
            
        Returns:
            True if parameters are valid, False otherwise.
        """
        return True
```

### Integrace NLP modelů

Pro integraci NLP modelů do Presidio je potřeba implementovat vlastní `NlpEngine` a `EntityRecognizer`.

**Příklad integrace XLM-RoBERTa modelu**:

```python
from typing import List, Optional, Tuple

import torch
from presidio_analyzer import EntityRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts
from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline

class XlmRobertaRecognizer(EntityRecognizer):
    """
    Recognizer that uses XLM-RoBERTa model for NER.
    """
    
    def __init__(
        self,
        model_path: str,
        supported_entities: List[str],
        threshold: float = 0.5
    ):
        self.model_path = model_path
        self.threshold = threshold
        
        # Load model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForTokenClassification.from_pretrained(model_path)
        self.ner_pipeline = pipeline(
            "ner",
            model=self.model,
            tokenizer=self.tokenizer,
            aggregation_strategy="simple"
        )
        
        super().__init__(
            supported_entities=supported_entities,
            name="XlmRobertaRecognizer"
        )
    
    def load(self) -> None:
        """Load the model, already done in __init__."""
        pass
    
    def analyze(
        self,
        text: str,
        entities: List[str],
        nlp_artifacts: Optional[NlpArtifacts] = None
    ) -> List[RecognizerResult]:
        """
        Analyze text using the XLM-RoBERTa model.
        
        Args:
            text: The text to analyze.
            entities: List of entities to look for.
            nlp_artifacts: NLP artifacts if available.
            
        Returns:
            List of RecognizerResult objects.
        """
        if not text:
            return []
        
        # Filter entities
        filtered_entities = [e for e in entities if e in self.supported_entities]
        if not filtered_entities:
            return []
        
        # Run NER pipeline
        ner_results = self.ner_pipeline(text)
        
        # Convert to RecognizerResult
        results = []
        for item in ner_results:
            entity_type = item["entity_group"]
            if entity_type in filtered_entities and item["score"] >= self.threshold:
                result = RecognizerResult(
                    entity_type=entity_type,
                    start=item["start"],
                    end=item["end"],
                    score=item["score"],
                    analysis_explanation=f"XLM-RoBERTa model detected {entity_type}"
                )
                results.append(result)
        
        return results
```

## Deployment

### Lokální deployment

Pro lokální vývoj a testování používáme Docker Compose:

```bash
# Spuštění všech služeb
docker-compose -f docker-compose.dev.yml up -d

# Spuštění konkrétní služby
docker-compose -f docker-compose.dev.yml up -d api

# Zobrazení logů
docker-compose -f docker-compose.dev.yml logs -f

# Zastavení všech služeb
docker-compose -f docker-compose.dev.yml down
```

### Staging deployment

Staging deployment je automatizován pomocí CI/CD pipeline:

1. Merge do `develop` větve spustí automatický deployment do staging prostředí.
2. Alternativně lze spustit manuální deployment z GitLab/GitHub UI.

### Produkční deployment

Produkční deployment je manuální proces:

1. Vytvoření release větve z `develop`:
   ```bash
   git checkout develop
   git pull
   git checkout -b release/X.Y.Z
   ```

2. Finalizace release (verze, changelog):
   ```bash
   # Aktualizace verze
   sed -i 's/version = "X.Y.Z-dev"/version = "X.Y.Z"/' pyproject.toml
   
   # Aktualizace changelog
   vi CHANGELOG.md
   
   git add pyproject.toml CHANGELOG.md
   git commit -m "Bump version to X.Y.Z"
   ```

3. Merge do `main` větve přes Merge Request.

4. Vytvoření tagu:
   ```bash
   git checkout main
   git pull
   git tag -a vX.Y.Z -m "Release X.Y.Z"
   git push origin vX.Y.Z
   ```

5. Spuštění produkčního deployment z GitLab/GitHub UI.

## Troubleshooting

### Známé problémy

- **Presidio a Python 3.11**: Některé verze Presidio mohou mít problémy s Python 3.11. Řešení: Použijte nejnovější verzi Presidio nebo přejděte na Python 3.10.
- **GPU akcelerace**: Pro GPU akcelerace NLP modelů je potřeba správná verze CUDA. Řešení: Zkontrolujte kompatibilitu PyTorch/CUDA.
- **Paměťové nároky**: XLM-RoBERTa model může mít vysoké paměťové nároky. Řešení: Použijte kvantizaci nebo menší model.

### Debugging

- **Logování**: Zvyšte úroveň logování pro detailnější informace:
  ```python
  import logging
  logging.basicConfig(level=logging.DEBUG)
  ```

- **Interaktivní debugging**: Použijte `pdb` nebo `ipdb` pro interaktivní debugging:
  ```python
  import pdb; pdb.set_trace()
  ```

- **Profiling**: Pro identifikaci výkonnostních problémů použijte:
  ```python
  import cProfile
  cProfile.run('function_to_profile()')
  ```

### Podpora

- **Interní podpora**: Kontaktujte tým přes Slack kanál `#meddocai-anonymizer`.
- **Externí zdroje**:
  - [Presidio dokumentace](https://microsoft.github.io/presidio/)
  - [Hugging Face dokumentace](https://huggingface.co/docs)
  - [FastAPI dokumentace](https://fastapi.tiangolo.com/)
