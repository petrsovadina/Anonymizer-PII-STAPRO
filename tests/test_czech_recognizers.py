"""
Testy pro české rozpoznávače entit
"""
import pytest
import sys
from pathlib import Path

# Přidání kořenového adresáře projektu do sys.path
# To umožní import modulů z adresářů jako 'recognizers', 'services' atd. přímo.
# /app/tests/test_czech_recognizers.py -> /app
root_path = Path(__file__).parent.parent
sys.path.append(str(root_path))

from recognizers.birth_number import CzechBirthNumberRecognizer
from recognizers.health_insurance import CzechHealthInsuranceNumberRecognizer
from recognizers.diagnosis_codes import CzechMedicalDiagnosisCodeRecognizer
from recognizers.medical_facilities import CzechMedicalFacilityRecognizer
from recognizers.czech_ico_recognizer import CzechICORecognizer # Import pro IČO

class TestCzechBirthNumberRecognizer:
    """Testy pro rozpoznávač českých rodných čísel"""
    
    @pytest.fixture
    def recognizer(self):
        """Fixture pro rozpoznávač rodných čísel"""
        return CzechBirthNumberRecognizer()
    
    def test_recognizer_initialization(self, recognizer):
        """Test inicializace rozpoznávače"""
        assert recognizer is not None
        assert "CZECH_BIRTH_NUMBER" in recognizer.supported_entities
    
    def test_valid_birth_number_detection(self, recognizer):
        """Test detekce validního rodného čísla"""
        text = "Pacient s rodným číslem 760506/1234 byl přijat."
        results = recognizer.analyze(text, ["CZECH_BIRTH_NUMBER"], None)
        assert len(results) > 0
        assert results[0].entity_type == "CZECH_BIRTH_NUMBER"
        assert "760506/1234" in text[results[0].start:results[0].end]
    
    def test_birth_number_validation(self, recognizer):
        """Test validace rodného čísla"""
        # Validní rodné číslo
        assert recognizer._is_valid_birth_number("760506/1234") == True
        
        # Nevalidní rodné číslo (špatný měsíc)
        assert recognizer._is_valid_birth_number("761306/1234") == False
        
        # Nevalidní rodné číslo (špatný den)
        assert recognizer._is_valid_birth_number("760532/1234") == False
    
    def test_birth_number_without_slash(self, recognizer):
        """Test detekce rodného čísla bez lomítka"""
        text = "Rodné číslo: 7605061234"
        results = recognizer.analyze(text, ["CZECH_BIRTH_NUMBER"], None)
        assert len(results) > 0

class TestCzechHealthInsuranceRecognizer:
    """Testy pro rozpoznávač čísel zdravotního pojištění"""
    
    @pytest.fixture
    def recognizer(self):
        """Fixture pro rozpoznávač pojištění"""
        return CzechHealthInsuranceNumberRecognizer()
    
    def test_recognizer_initialization(self, recognizer):
        """Test inicializace rozpoznávače"""
        assert recognizer is not None
        assert "CZECH_HEALTH_INSURANCE_NUMBER" in recognizer.supported_entities

class TestCzechDiagnosisCodeRecognizer:
    """Testy pro rozpoznávač kódů diagnóz"""
    
    @pytest.fixture
    def recognizer(self):
        """Fixture pro rozpoznávač diagnóz"""
        return CzechMedicalDiagnosisCodeRecognizer()
    
    def test_recognizer_initialization(self, recognizer):
        """Test inicializace rozpoznávače"""
        assert recognizer is not None
        assert "CZECH_DIAGNOSIS_CODE" in recognizer.supported_entities
    
    def test_icd10_code_detection(self, recognizer):
        """Test detekce ICD-10 kódů"""
        text = "Diagnóza: J45.0 - Asthma bronchiale"
        results = recognizer.analyze(text, ["CZECH_DIAGNOSIS_CODE"], None)
        assert len(results) > 0
        assert results[0].entity_type == "CZECH_DIAGNOSIS_CODE"

class TestCzechMedicalFacilityRecognizer:
    """Testy pro rozpoznávač zdravotnických zařízení"""
    
    @pytest.fixture
    def recognizer(self):
        """Fixture pro rozpoznávač zařízení"""
        return CzechMedicalFacilityRecognizer()
    
    def test_recognizer_initialization(self, recognizer):
        """Test inicializace rozpoznávače"""
        assert recognizer is not None
        assert "CZECH_MEDICAL_FACILITY" in recognizer.supported_entities
    
    def test_hospital_detection(self, recognizer):
        """Test detekce nemocnic"""
        text = "Přijat do Fakultní nemocnice v Motole"
        results = recognizer.analyze(text, ["CZECH_MEDICAL_FACILITY"], None)
        assert len(results) > 0
        assert results[0].entity_type == "CZECH_MEDICAL_FACILITY"

class TestCzechICORecognizer:
    """Testy pro rozpoznávač českých IČO"""

    @pytest.fixture
    def recognizer(self):
        """Fixture pro rozpoznávač IČO"""
        return CzechICORecognizer()

    def test_recognizer_initialization(self, recognizer):
        """Test inicializace rozpoznávače"""
        assert recognizer is not None
        assert "CZECH_ICO" in recognizer.supported_entities
        assert recognizer.name == "Czech ICO Recognizer"

    @pytest.mark.parametrize(
        "text, expected_icos",
        [
            ("Firma má IČO: 00027383.", ["00027383"]),
            ("IČO 00023221 patří Národní knihovně.", ["00023221"]),
            ("Platná IČO jsou 00027383 a 00023221.", ["00027383", "00023221"]),
            ("Text bez IČO.", []),
            ("IČO: 12345678 (neplatné).", []), # Toto IČO je neplatné dle kontrolního součtu
            ("IČO: 00027383, ale také 12345670 (neplatné).", ["00027383"]),
            ("Krátké IČO 1234567.", []),
            ("Dlouhé IČO 123456789.", []),
            ("IČO s písmeny 1234567X.", []),
        ],
    )
    def test_ico_detection(self, recognizer, text, expected_icos):
        """Test detekce různých IČO scénářů"""
        results = recognizer.analyze(text, entities=["CZECH_ICO"], nlp_artifacts=None)
        assert len(results) == len(expected_icos)

        detected_texts = [text[res.start:res.end] for res in results]
        for expected_ico in expected_icos:
            assert expected_ico in detected_texts

    def test_valid_ico_checksum(self, recognizer):
        """Test validace kontrolního součtu pro platná IČO"""
        assert recognizer._is_valid_ico("00027383")  # Česká televize
        assert recognizer._is_valid_ico("00023221")  # Národní knihovna ČR
        assert recognizer._is_valid_ico("27082440")  # Seznam.cz
        assert recognizer._is_valid_ico("45274649")  # Alza.cz

    def test_invalid_ico_checksum(self, recognizer):
        """Test validace kontrolního součtu pro neplatná IČO"""
        assert not recognizer._is_valid_ico("12345678") # Můj původní test, špatný checksum
        assert not recognizer._is_valid_ico("00027384") # Poslední číslice špatně
        assert not recognizer._is_valid_ico("12345670") # Jiné neplatné
        assert not recognizer._is_valid_ico("00000000")

    def test_ico_format_validation(self, recognizer):
        """Test validace formátu IČO (délka, číslice)"""
        assert not recognizer._is_valid_ico("1234567")   # Příliš krátké
        assert not recognizer._is_valid_ico("123456789") # Příliš dlouhé
        assert not recognizer._is_valid_ico("1234567X")  # Obsahuje písmeno
        assert not recognizer._is_valid_ico("123 45678") # Obsahuje mezeru

    def test_context_score_boost(self, recognizer):
        """Test zvýšení skóre při přítomnosti kontextových slov"""
        text_no_context = "Číslo 00027383 bylo nalezeno."
        text_with_context = "Identifikační číslo firmy je 00027383." # "Identifikační číslo", "firmy"

        results_no_context = recognizer.analyze(text_no_context, entities=["CZECH_ICO"], nlp_artifacts=None)
        assert len(results_no_context) == 1
        score_no_context = results_no_context[0].score
        assert score_no_context == recognizer.DEFAULT_SCORE

        results_with_context = recognizer.analyze(text_with_context, entities=["CZECH_ICO"], nlp_artifacts=None)
        assert len(results_with_context) == 1
        score_with_context = results_with_context[0].score
        assert score_with_context > score_no_context
        assert score_with_context == min(1.0, recognizer.DEFAULT_SCORE + recognizer.CONTEXT_SCORE_BOOST)

    def test_no_false_positives_on_similar_numbers(self, recognizer):
        """Test, aby se nerozpoznávala jiná 8místná čísla jako IČO, pokud nesplňují kontrolní součet."""
        text = "Telefonní číslo je 12345678, bankovní účet 87654321."
        # Předpokládáme, že tato čísla nejsou validní IČO (což pro 12345678 a 87654321 platí)
        results = recognizer.analyze(text, entities=["CZECH_ICO"], nlp_artifacts=None)
        assert len(results) == 0
