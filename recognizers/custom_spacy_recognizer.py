from typing import List, Optional

from presidio_analyzer import EntityRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts

class CustomSpacyRecognizerCs(EntityRecognizer):
    """
    Vlastní (minimální) SpacyRecognizer pro jazyk 'cs'.
    Cílem je přebít defaultní SpacyRecognizer pro 'cs', který může způsobovat
    problémy s modelem xx_ent_wiki_sm kvůli přístupu k nlp_artifacts.doc.
    Tento recognizer buď neudělá nic, nebo bezpečně zpracuje nlp_artifacts.entities.
    Prozatím bude vracet prázdný seznam, aby se zabránilo chybě.
    Entity z NLP modelu pro 'cs' (specificky PERSON) jsou zpracovávány
    prostřednictvím CzechNameRecognizer.
    """

    def __init__(
        self,
        supported_entities: Optional[List[str]] = None,
        supported_language: str = "cs",
        name: str = "SpacyRecognizer",  # Musí se jmenovat stejně jako defaultní
        **kwargs,
    ):
        _supported_entities = supported_entities if supported_entities else ["LOC", "ORG", "MISC", "PERSON", "DATE", "TIME", "NUMBER", "IP_ADDRESS", "EMAIL_ADDRESS", "URL", "PHONE_NUMBER", "CREDIT_CARD", "CRYPTO", "IBAN_CODE", "MEDICAL_LICENSE", "US_SSN", "US_PASSPORT", "US_DRIVER_LICENSE", "US_ITIN", "US_BANK_NUMBER"] # Široká škála pro jistotu

        super().__init__(
            supported_entities=_supported_entities,
            supported_language=supported_language,
            name=name,
            **kwargs,
        )
        print(f"CustomSpacyRecognizerCs: INITIALIZED for language '{supported_language}', name '{name}', entities {self.supported_entities}")

    def load(self) -> None:
        pass

    def analyze(
        self, text: str, entities: List[str], nlp_artifacts: NlpArtifacts
    ) -> List[RecognizerResult]:
        """
        Tato metoda je volána AnalyzerEngine. Vrací prázdný seznam, aby se zabránilo
        přístupu k nlp_artifacts.doc, který způsobuje chybu s xx_ent_wiki_sm.
        """
        print(f"CustomSpacyRecognizerCs ({self.name}/{self.supported_language}): ANALYZE CALLED.")
        print(f"  Entities requested for analysis: {entities}")
        print(f"  Text snippet: '{text[:80]}...'")

        if nlp_artifacts:
            # print(f"  NLP Artifacts available. Keys: {nlp_artifacts.to_dict().keys()}") # Tento řádek způsobuje AttributeError
            print(f"  NLP Artifacts - raw entities: {nlp_artifacts.entities}")
            # Zkusíme bezpečně přistoupit k atributu 'doc', abychom viděli, zda existuje
            if hasattr(nlp_artifacts, 'doc') and nlp_artifacts.doc is not None:
                print(f"  NLP Artifacts HAS attribute 'doc'. Type: {type(nlp_artifacts.doc)}")
            else:
                print("  NLP Artifacts does NOT have attribute 'doc' or it is None.")
        else:
            print("  NLP Artifacts are None.")

        # Vracíme prázdný seznam, abychom se vyhnuli chybě a nechali ostatní rozpoznávače pracovat.
        # Zejména CzechNameRecognizer by měl zpracovat PERSON entity z nlp_artifacts.entities.
        print(f"CustomSpacyRecognizerCs ({self.name}/{self.supported_language}): Returning [] to avoid potential 'nlp_artifacts.doc' error.")
        return []
