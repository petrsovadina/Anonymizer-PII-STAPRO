import re
from typing import List, Optional

from presidio_analyzer import EntityRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts

class CzechPassRecognizer(EntityRecognizer):
    """
    Rozpoznávač pro čísla českých cestovních pasů (CP).
    Pokrývá běžné formáty: 1 písmeno + 8 číslic, nebo 9 číslic.
    """

    # Regex pro 1 velké písmeno následované 8 číslicemi
    PASS_REGEX_ALPHANUM = r"\b([A-Z]\d{8})\b"
    # Regex pro 9 číslic (může se vyskytovat, i když méně typické pro nejnovější pasy než alfanum.)
    PASS_REGEX_NUMERIC = r"\b(\d{9})\b"

    CONTEXT_WORDS = [
        "pas", "cestovní pas", "číslo pasu", "č. pasu", "CP", "cestovního pasu", "passport no", "passport number"
    ]

    DEFAULT_SCORE_ALPHANUM = 0.80 # Dobré skóre pro specifický alfanumerický formát
    DEFAULT_SCORE_NUMERIC = 0.55  # Nižší skóre pro čistě číselný formát (podobné OP, tel. číslu)
    CONTEXT_SCORE_BOOST = 0.25

    def __init__(
        self,
        supported_entities: Optional[List[str]] = None,
        supported_language: str = "cs",
        **kwargs,
    ):
        self.supported_entities = supported_entities if supported_entities else ["CZECH_PASSPORT_NUMBER"]
        super().__init__(
            supported_entities=self.supported_entities,
            supported_language=supported_language,
            name="Czech Passport Recognizer",
            context=self.CONTEXT_WORDS,
            **kwargs,
        )
        self.pass_pattern_alphanum = re.compile(self.PASS_REGEX_ALPHANUM)
        self.pass_pattern_numeric = re.compile(self.PASS_REGEX_NUMERIC)

    def load(self) -> None:
        pass

    def analyze(
        self, text: str, entities: List[str], nlp_artifacts: NlpArtifacts
    ) -> List[RecognizerResult]:
        results = []

        # Hledání alfanumerického formátu (Písmeno následované 8 číslicemi)
        for match in self.pass_pattern_alphanum.finditer(text):
            start, end = match.span()
            pass_text = match.group(1)
            score = self.DEFAULT_SCORE_ALPHANUM

            text_before = text[max(0, start - 50):start].lower()
            text_after = text[end:min(len(text), end + 20)].lower()
            context_found = False
            for word in self.context:
                if word.lower() in text_before or word.lower() in text_after:
                    score = min(1.0, score + self.CONTEXT_SCORE_BOOST)
                    context_found = True
                    break

            # DEBUG:
            # print(f"CzechPassRecognizer DEBUG (alphanum): Match '{pass_text}', Score: {score}, Context: {context_found}")

            results.append(
                RecognizerResult(
                    entity_type="CZECH_PASSPORT_NUMBER",
                    start=start,
                    end=end,
                    score=score,
                    analysis_explanation=f"Found Czech Passport (alphanum): {pass_text}",
                    recognition_metadata={
                        RecognizerResult.RECOGNIZER_NAME_KEY: self.name,
                        RecognizerResult.RECOGNIZER_IDENTIFIER_KEY: self.id
                    }
                )
            )

        # Hledání číselného formátu (9 číslic)
        for match in self.pass_pattern_numeric.finditer(text):
            start, end = match.span()
            pass_text = match.group(1)

            is_overlapping_with_better_alphanum = False
            for res in results: # Kontrola vůči již nalezeným alfanumerickým pasům
                if res.entity_type == "CZECH_PASSPORT_NUMBER" and \
                   (match.start() >= res.start and match.end() <= res.end and res.score > self.DEFAULT_SCORE_NUMERIC):
                    is_overlapping_with_better_alphanum = True
                    break
            if is_overlapping_with_better_alphanum:
                continue

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
            # print(f"CzechPassRecognizer DEBUG (numeric): Match '{pass_text}', Score: {score}, Context: {context_found}, Overlap: {is_overlapping_with_better_alphanum}")

            if score > 0.5: # Prahová hodnota pro numerický pas
                results.append(
                    RecognizerResult(
                        entity_type="CZECH_PASSPORT_NUMBER",
                        start=start,
                        end=end,
                        score=score,
                        analysis_explanation=f"Found Czech Passport (numeric): {pass_text}",
                        recognition_metadata={
                            RecognizerResult.RECOGNIZER_NAME_KEY: self.name,
                            RecognizerResult.RECOGNIZER_IDENTIFIER_KEY: self.id
                        }
                    )
                )

        final_results = []
        seen_spans = set()
        for res in sorted(results, key=lambda x: x.start):
            if (res.start, res.end) not in seen_spans:
                final_results.append(res)
                seen_spans.add((res.start, res.end))

        return final_results
