import logging
from typing import List, Optional

from presidio_analyzer import RecognizerRegistry
from presidio_analyzer.predefined_recognizers import EmailRecognizer # Import EmailRecognizer
from .birth_number import CzechBirthNumberRecognizer
from .health_insurance import CzechHealthInsuranceNumberRecognizer
from .diagnosis_codes import CzechMedicalDiagnosisCodeRecognizer
from .medical_facilities import CzechMedicalFacilityRecognizer
from .names import CzechNameRecognizer
from .addresses import CzechAddressRecognizer
from .phone_numbers import CzechPhoneNumberRecognizer
from .bank_accounts import CzechBankAccountRecognizer
from .czech_ico_recognizer import CzechICORecognizer # Přidán import pro IČO
from .czech_dic_recognizer import CzechDICRecognizer # Přidán import pro DIČ
from .czech_op_recognizer import CzechOPRecognizer # Přidán import pro OP
from .czech_pass_recognizer import CzechPassRecognizer # Přidán import pro Pasy
from .czech_rp_recognizer import CzechRPRecognizer # Přidán import pro ŘP
from .custom_spacy_recognizer import CustomSpacyRecognizerCs # Nový import

# Nastavení loggeru
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class CzechRecognizerRegistry:
    """
    Registr specializovaných českých rozpoznávačů pro Presidio.
    """
    
    @staticmethod
    def register_czech_recognizers(registry: RecognizerRegistry) -> None:
        """
        Registruje specializované české rozpoznávače do Presidio registru.
        
        Args:
            registry: Presidio registr rozpoznávačů
        """
        logger.info("Registering specialized Czech recognizers")
        
        # Vytvoření a registrace rozpoznávače českých rodných čísel
        birth_number_recognizer = CzechBirthNumberRecognizer()
        registry.add_recognizer(birth_number_recognizer)
        logger.info(f"Registered: {birth_number_recognizer.name}")
        
        # Vytvoření a registrace rozpoznávače českých čísel pojištěnce
        health_insurance_recognizer = CzechHealthInsuranceNumberRecognizer()
        registry.add_recognizer(health_insurance_recognizer)
        logger.info(f"Registered: {health_insurance_recognizer.name}")
        
        # Vytvoření a registrace rozpoznávače českých kódů diagnóz
        diagnosis_code_recognizer = CzechMedicalDiagnosisCodeRecognizer()
        registry.add_recognizer(diagnosis_code_recognizer)
        logger.info(f"Registered: {diagnosis_code_recognizer.name}")
        
        # Vytvoření a registrace rozpoznávače českých zdravotnických zařízení
        medical_facility_recognizer = CzechMedicalFacilityRecognizer()
        registry.add_recognizer(medical_facility_recognizer)
        logger.info(f"Registered: {medical_facility_recognizer.name}")

        # Vytvoření a registrace CustomSpacyRecognizerCs pro 'cs'
        # Měl by být registrován před CzechNameRecognizer, pokud by CzechNameRecognizer
        # také cílil na obecné NER entity a chtěli bychom specifikovat pořadí.
        # V našem případě je to hlavně pro "přebití" defaultního SpacyRecognizer pro 'cs'.
        custom_spacy_cs = CustomSpacyRecognizerCs()
        registry.add_recognizer(custom_spacy_cs)
        logger.info(f"Registered: {custom_spacy_cs.name} for language 'cs' (custom override)")

        # Vytvoření a registrace rozpoznávače českých jmen
        name_recognizer = CzechNameRecognizer()
        registry.add_recognizer(name_recognizer)
        logger.info(f"Registered: {name_recognizer.name}")

        # Vytvoření a registrace rozpoznávače českých adres
        address_recognizer = CzechAddressRecognizer()
        registry.add_recognizer(address_recognizer)
        logger.info(f"Registered: {address_recognizer.name}")

        # Vytvoření a registrace rozpoznávače českých telefonních čísel
        phone_recognizer = CzechPhoneNumberRecognizer()
        registry.add_recognizer(phone_recognizer)
        logger.info(f"Registered: {phone_recognizer.name}")

        # Vytvoření a registrace defaultního EmailRecognizer
        # EmailRecognizer standardně podporuje 'en', ale je jazykově agnostický.
        # Přidáním do registru, který podporuje 'cs', umožníme jeho použití i pro české texty.
        email_recognizer = EmailRecognizer() # Odstraněn supported_languages
        registry.add_recognizer(email_recognizer)
        logger.info(f"Registered: {email_recognizer.name} (default lang: {email_recognizer.supported_language})")

        # Vytvoření a registrace rozpoznávače českých bankovních účtů
        bank_account_recognizer = CzechBankAccountRecognizer()
        registry.add_recognizer(bank_account_recognizer)
        logger.info(f"Registered: {bank_account_recognizer.name}")

        # Vytvoření a registrace rozpoznávače českých IČO
        ico_recognizer = CzechICORecognizer()
        registry.add_recognizer(ico_recognizer)
        logger.info(f"Registered: {ico_recognizer.name}")

        # Vytvoření a registrace rozpoznávače českých DIČ
        dic_recognizer = CzechDICRecognizer()
        registry.add_recognizer(dic_recognizer)
        logger.info(f"Registered: {dic_recognizer.name}")

        # Vytvoření a registrace rozpoznávače českých čísel OP
        op_recognizer = CzechOPRecognizer()
        registry.add_recognizer(op_recognizer)
        logger.info(f"Registered: {op_recognizer.name}")

        # Vytvoření a registrace rozpoznávače českých čísel pasů
        pass_recognizer = CzechPassRecognizer()
        registry.add_recognizer(pass_recognizer)
        logger.info(f"Registered: {pass_recognizer.name}")

        # Vytvoření a registrace rozpoznávače českých čísel ŘP
        rp_recognizer = CzechRPRecognizer()
        registry.add_recognizer(rp_recognizer)
        logger.info(f"Registered: {rp_recognizer.name}")
        
        # Zde budou přidány další specializované české rozpoznávače
        
        logger.info("All Czech recognizers registered successfully")
    
    @staticmethod
    def get_supported_entities() -> List[str]:
        """
        Vrátí seznam všech podporovaných entit českými rozpoznávači.
        
        Returns:
            Seznam podporovaných entit
        """
        return [
            "CZECH_BIRTH_NUMBER",
            "CZECH_HEALTH_INSURANCE_NUMBER",
            "CZECH_DIAGNOSIS_CODE",
            "CZECH_MEDICAL_FACILITY",
            "PERSON", # Přidáno pro CzechNameRecognizer
            "CZECH_ADDRESS", # Přidáno pro CzechAddressRecognizer
            "CZECH_PHONE_NUMBER", # Přidáno pro CzechPhoneNumberRecognizer
            "EMAIL_ADDRESS", # Přidáno pro EmailRecognizer
            "CZECH_BANK_ACCOUNT_NUMBER", # Přidáno pro CzechBankAccountRecognizer
            "CZECH_ICO", # Přidáno pro CzechICORecognizer
            "CZECH_DIC", # Přidáno pro CzechDICRecognizer
            "CZECH_OP_NUMBER", # Přidáno pro CzechOPRecognizer
            "CZECH_PASSPORT_NUMBER", # Přidáno pro CzechPassRecognizer
            "CZECH_RP_NUMBER", # Přidáno pro CzechRPRecognizer
            # Zde budou přidány další entity
        ]
