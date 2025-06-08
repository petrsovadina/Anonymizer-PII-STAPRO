import re
from typing import List, Optional

from presidio_analyzer import EntityRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts

class CzechBankAccountRecognizer(EntityRecognizer):
    """
    Rozpoznávač českých čísel bankovních účtů.
    Formáty: [předčíslí-]číslo/kód banky
    Předčíslí: 1-6 číslic (volitelné)
    Číslo: 2-10 číslic
    Kód banky: 4 číslice
    """

    # Regex pro česká čísla bankovních účtů:
    # \b                     - Hranice slova
    # (?:(\d{1,6})-)?       - Volitelná skupina pro předčíslí (1-6 číslic) následované pomlčkou.
    #                          Předčíslí je zachyceno ve skupině 1.
    # (\d{2,10})            - Hlavní číslo účtu (2-10 číslic), zachyceno ve skupině 2.
    # \/                     - Lomítko oddělující číslo účtu a kód banky.
    # (\d{4})                - Kód banky (přesně 4 číslice), zachyceno ve skupině 3.
    # \b                     - Hranice slova
    ACCOUNT_REGEX = r"\b(?:(\d{1,6})-)?(\d{2,10})\/(\d{4})\b"

    CONTEXT_WORDS = [
        "účet", "účtu", "č.ú.", "číslo účtu", "bankovní účet", "bankovního účtu",
        "účet číslo", "bankovní spojení", "platba na", "úhrada na"
    ]

    DEFAULT_SCORE = 0.75  # Základní skóre
    CONTEXT_SCORE_BOOST = 0.20 # Zvýšení skóre při nalezení kontextového slova

    def __init__(
        self,
        supported_entities: Optional[List[str]] = None,
        supported_language: str = "cs",
        **kwargs,
    ):
        self.supported_entities = supported_entities if supported_entities else ["CZECH_BANK_ACCOUNT_NUMBER"]
        super().__init__(
            supported_entities=self.supported_entities,
            supported_language=supported_language,
            name="Czech Bank Account Recognizer",
            context=self.CONTEXT_WORDS,
            **kwargs,
        )
        self.account_pattern = re.compile(self.ACCOUNT_REGEX)

    def load(self) -> None:
        """Načtení modelu - není potřeba pro tento regex-based recognizer."""
        pass

    def analyze(
        self, text: str, entities: List[str], nlp_artifacts: NlpArtifacts
    ) -> List[RecognizerResult]:
        results = []
        for match in self.account_pattern.finditer(text):
            start, end = match.span()
            account_text = match.group(0) # Celý text shody
            prefix = match.group(1)       # Předčíslí (může být None)
            main_number = match.group(2)  # Hlavní číslo
            bank_code = match.group(3)    # Kód banky

            # Základní validace délek (regex by to měl pokrýt, ale pro jistotu)
            if prefix and not (1 <= len(prefix) <= 6):
                continue
            if not (2 <= len(main_number) <= 10):
                continue
            if len(bank_code) != 4: # Kód banky musí mít 4 číslice
                continue

            # Výpočet skóre na základě kontextu
            score = self.DEFAULT_SCORE
            text_before = text[max(0, start - 50):start].lower() # Okno 50 znaků před
            text_after = text[end:min(len(text), end + 20)].lower() # Okno 20 znaků za

            for word in self.context:
                if word.lower() in text_before or word.lower() in text_after:
                    score = min(1.0, score + self.CONTEXT_SCORE_BOOST)
                    break

            # Vytvoření RecognizerResult
            results.append(
                RecognizerResult(
                    entity_type="CZECH_BANK_ACCOUNT_NUMBER",
                    start=start,
                    end=end,
                    score=score,
                    analysis_explanation=f"Found Czech bank account: {account_text}",
                    recognition_metadata={
                        "prefix": prefix if prefix else "",
                        "account_number_main": main_number,
                        "bank_code": bank_code,
                        RecognizerResult.RECOGNIZER_NAME_KEY: self.name,
                        RecognizerResult.RECOGNIZER_IDENTIFIER_KEY: self.id
                    }
                )
            )
        return results
