import re
from typing import List, Optional

from presidio_analyzer import EntityRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts


class CzechICORecognizer(EntityRecognizer):
    """
    Rozpoznávač pro česká IČO (Identifikační číslo osoby).
    IČO je 8místné číslo.
    """

    ICO_REGEX = r"\b(\d{8})\b"
    CONTEXT_WORDS = [
        "IČO", "IČ", "Identifikační číslo", "firmy", "organizace"
    ]

    DEFAULT_SCORE = 0.8  # Základní skóre pro IČO
    CONTEXT_SCORE_BOOST = 0.15

    def __init__(
        self,
        supported_entities: Optional[List[str]] = None,
        supported_language: str = "cs",
        **kwargs,
    ):
        self.supported_entities = supported_entities if supported_entities else ["CZECH_ICO"]
        super().__init__(
            supported_entities=self.supported_entities,
            supported_language=supported_language,
            name="Czech ICO Recognizer",
            context=self.CONTEXT_WORDS,
            **kwargs,
        )
        self.ico_pattern = re.compile(self.ICO_REGEX)

    def load(self) -> None:
        """Načtení modelu - není potřeba pro tento regex-based recognizer."""
        pass

    def analyze(
        self, text: str, entities: List[str], nlp_artifacts: NlpArtifacts
    ) -> List[RecognizerResult]:
        results = []
        for match in self.ico_pattern.finditer(text):
            start, end = match.span()
            ico_text = match.group(1)

            # Jednoduchá kontrola (IČO by mělo být přesně 8 číslic - regex to již zajišťuje)
            # if not (len(ico_text) == 8 and ico_text.isdigit()):
            #     continue

            # Validace IČO (kontrolní součet modulo 11)
            if not self._is_valid_ico(ico_text):
                continue

            score = self.DEFAULT_SCORE
            text_before = text[max(0, start - 30):start].lower()
            text_after = text[end:min(len(text), end + 10)].lower()

            for word in self.context:
                if word.lower() in text_before or word.lower() in text_after:
                    score = min(1.0, score + self.CONTEXT_SCORE_BOOST)
                    break

            results.append(
                RecognizerResult(
                    entity_type="CZECH_ICO",
                    start=start,
                    end=end,
                    score=score,
                    analysis_explanation=f"Found Czech ICO: {ico_text}",
                    recognition_metadata={
                        RecognizerResult.RECOGNIZER_NAME_KEY: self.name,
                        RecognizerResult.RECOGNIZER_IDENTIFIER_KEY: self.id
                    }
                )
            )
        return results

    def _is_valid_ico(self, ico: str) -> bool:
        """Ověří platnost IČO pomocí kontrolního součtu (váhy 8,7,6,5,4,3,2)."""
        if not (len(ico) == 8 and ico.isdigit()):
            return False

        weights = [8, 7, 6, 5, 4, 3, 2]
        s = sum(int(ico[i]) * weights[i] for i in range(7))
        checksum = (11 - (s % 11)) % 10

        return checksum == int(ico[7])
