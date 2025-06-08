import re
from typing import List, Optional

from presidio_analyzer import EntityRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts

# Potenciálně pro validaci můžeme potřebovat metody z ostatních rozpoznávačů
# from .czech_ico_recognizer import CzechICORecognizer
# from .birth_number import CzechBirthNumberRecognizer

class CzechDICRecognizer(EntityRecognizer):
    """
    Rozpoznávač pro česká DIČ (Daňové identifikační číslo).
    Formát: CZ následované 8-10 číslicemi (IČO nebo rodné číslo).
    """

    # Regex pro DIČ: CZ následované 8, 9 nebo 10 číslicemi.
    # Pro rodné číslo může být za lomítkem, ale DIČ se obvykle uvádí bez lomítka.
    # Tento regex zachytí CZXXXXXXXX, CZXXXXXXXXX, CZXXXXXXXXXX
    DIC_REGEX = r"\b(CZ\d{8,10})\b"
    CONTEXT_WORDS = [
        "DIČ", "Daňové identifikační číslo", "VAT ID", "VAT number", "IČ DPH"
    ]

    DEFAULT_SCORE = 0.85  # Návrat k původnímu základnímu skóre
    CONTEXT_SCORE_BOOST = 0.10 # Návrat k původnímu kontextovému boostu

    def __init__(
        self,
        supported_entities: Optional[List[str]] = None,
        supported_language: str = "cs",
        **kwargs,
    ):
        self.supported_entities = supported_entities if supported_entities else ["CZECH_DIC"]
        # self.ico_recognizer = CzechICORecognizer() # Pro případnou validaci
        # self.birth_recognizer = CzechBirthNumberRecognizer() # Pro případnou validaci

        super().__init__(
            supported_entities=self.supported_entities,
            supported_language=supported_language,
            name="Czech DIC Recognizer",
            context=self.CONTEXT_WORDS,
            **kwargs,
        )
        self.dic_pattern = re.compile(self.DIC_REGEX)

    def load(self) -> None:
        pass

    def analyze(
        self, text: str, entities: List[str], nlp_artifacts: NlpArtifacts
    ) -> List[RecognizerResult]:
        results = []
        for match in self.dic_pattern.finditer(text):
            start, end = match.span()
            dic_text = match.group(1)
            numerical_part = dic_text[2:] # Část za "CZ"

            # Základní validace délky numerické části (již pokryto regexem, ale pro přehlednost)
            if not (8 <= len(numerical_part) <= 10 and numerical_part.isdigit()):
                continue

            # Zde by mohla být přidána pokročilejší validace:
            # 1. Pokud má 8 číslic, ověřit jako IČO: self.ico_recognizer._is_valid_ico(numerical_part)
            # 2. Pokud má 9 nebo 10 číslic, ověřit jako rodné číslo: self.birth_recognizer._is_valid_birth_number(numerical_part)
            # Prozatím necháme bez této pokročilé validace, aby se předešlo složitostem s instanciací
            # a voláním metod jiných rozpoznávačů přímo zde.
            # Místo toho se spoléháme na to, že IČO a RČ budou rozpoznány svými vlastními rozpoznávači.
            # Tento rozpoznávač se soustředí na formát DIČ.

            score = self.DEFAULT_SCORE
            text_before = text[max(0, start - 40):start].lower()
            text_after = text[end:min(len(text), end + 20)].lower()

            for word in self.context:
                if word.lower() in text_before or word.lower() in text_after:
                    score = min(1.0, score + self.CONTEXT_SCORE_BOOST)
                    break

            # DEBUG: Vypíšeme nalezenou shodu a vypočítané skóre
            # print(f"CzechDICRecognizer DEBUG: Match found: '{dic_text}', Raw Score: {self.DEFAULT_SCORE}, Context Score: {score}, Context words: {self.CONTEXT_WORDS}")

            results.append(
                RecognizerResult(
                    entity_type="CZECH_DIC",
                    start=start,
                    end=end,
                    score=score,
                    analysis_explanation=f"Found Czech DIC: {dic_text}",
                    recognition_metadata={
                        RecognizerResult.RECOGNIZER_NAME_KEY: self.name,
                        RecognizerResult.RECOGNIZER_IDENTIFIER_KEY: self.id,
                        "vat_id_country": "CZ",
                        "vat_id_number": numerical_part
                    }
                )
            )
        return results
