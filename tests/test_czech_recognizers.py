"""
Testy pro české rozpoznávače entit
"""
import pytest
from czech_birth_number_recognizer import CzechBirthNumberRecognizer
from czech_health_insurance_recognizer import CzechHealthInsuranceNumberRecognizer
from czech_diagnosis_code_recognizer import CzechMedicalDiagnosisCodeRecognizer
from czech_medical_facility_recognizer import CzechMedicalFacilityRecognizer

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
