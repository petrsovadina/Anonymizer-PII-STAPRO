import re
from typing import List, Optional

from presidio_analyzer import EntityRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts

class CzechRPRecognizer(EntityRecognizer):
    """
    Rozpoznávač pro čísla českých řidičských průkazů (ŘP).
    Zaměřuje se na formát 8 číslic.
    """

    # Regex pro 8 číslic
    RP_REGEX_NUMERIC = r"\b(\d{8})\b"

    CONTEXT_WORDS = [
        "ŘP", "řidičský průkaz", "číslo ŘP", "č. ŘP", "řidičského průkazu",
        "řidičák", "řidičáku", "driving license no", "driver's license number"
    ]

    DEFAULT_SCORE_NUMERIC = 0.4  # Velmi nízké skóre pro krátký numerický formát bez kontextu
    CONTEXT_SCORE_BOOST = 0.4    # Výrazný boost při nalezení kontextu

    def __init__(
        self,
        supported_entities: Optional[List[str]] = None,
        supported_language: str = "cs",
        **kwargs,
    ):
        self.supported_entities = supported_entities if supported_entities else ["CZECH_RP_NUMBER"]
        super().__init__(
            supported_entities=self.supported_entities,
            supported_language=supported_language,
            name="Czech RP Recognizer",
            context=self.CONTEXT_WORDS,
            **kwargs,
        )
        self.rp_pattern_numeric = re.compile(self.RP_REGEX_NUMERIC)

    def load(self) -> None:
        pass

    def analyze(
        self, text: str, entities: List[str], nlp_artifacts: NlpArtifacts
    ) -> List[RecognizerResult]:
        results = []

        for match in self.rp_pattern_numeric.finditer(text):
            start, end = match.span()
            rp_text = match.group(1)

            score = self.DEFAULT_SCORE_NUMERIC
            text_before = text[max(0, start - 50):start].lower()
            text_after = text[end:min(len(text), end + 20)].lower()
            context_found = False
            for word in self.context:
                if word.lower() in text_before or word.lower() in text_after:
                    score = min(1.0, score + self.CONTEXT_SCORE_BOOST)
                    context_found = True
                    break

            # DEBUG:
            # print(f"CzechRPRecognizer DEBUG: Match '{rp_text}', Score: {score}, Context: {context_found}")

            # Prahová hodnota pro uznání ŘP, i s kontextem by skóre mělo být dostatečné
            if score > 0.6:
                results.append(
                    RecognizerResult(
                        entity_type="CZECH_RP_NUMBER",
                        start=start,
                        end=end,
                        score=score,
                        analysis_explanation=f"Found Czech RP (numeric): {rp_text}, Context: {context_found}",
                        recognition_metadata={
                            RecognizerResult.RECOGNIZER_NAME_KEY: self.name,
                            RecognizerResult.RECOGNIZER_IDENTIFIER_KEY: self.id
                        }
                    )
                )

        return results
