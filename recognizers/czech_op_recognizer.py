import re
from typing import List, Optional

from presidio_analyzer import EntityRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts

class CzechOPRecognizer(EntityRecognizer):
    """
    Rozpoznávač pro čísla českých občanských průkazů (OP).
    Pokrývá běžné moderní formáty: 9 číslic nebo 2 písmena následovaná 7 číslicemi.
    """

    # Regex pro 9 číslic (běžné u starších OP karet)
    OP_REGEX_NUMERIC = r"\b(\d{9})\b"
    # Regex pro 2 velká písmena následovaná 7 číslicemi (běžné u eOP)
    OP_REGEX_ALPHANUM = r"\b([A-Z]{2}\d{7})\b"

    CONTEXT_WORDS = [
        "OP", "občanský průkaz", "číslo OP", "č. OP", "č.OP", "občanského průkazu",
        "občanky", "občanka", "doklad totožnosti"
    ]

    DEFAULT_SCORE_NUMERIC = 0.6  # Nižší skóre pro čistě číselný formát kvůli možné kolizi
    DEFAULT_SCORE_ALPHANUM = 0.75 # Vyšší skóre pro alfanumerický formát
    CONTEXT_SCORE_BOOST = 0.25

    def __init__(
        self,
        supported_entities: Optional[List[str]] = None,
        supported_language: str = "cs",
        **kwargs,
    ):
        self.supported_entities = supported_entities if supported_entities else ["CZECH_OP_NUMBER"]
        super().__init__(
            supported_entities=self.supported_entities,
            supported_language=supported_language,
            name="Czech OP Recognizer",
            context=self.CONTEXT_WORDS,
            **kwargs,
        )
        self.op_pattern_numeric = re.compile(self.OP_REGEX_NUMERIC)
        self.op_pattern_alphanum = re.compile(self.OP_REGEX_ALPHANUM)

    def load(self) -> None:
        pass

    def analyze(
        self, text: str, entities: List[str], nlp_artifacts: NlpArtifacts
    ) -> List[RecognizerResult]:
        results = []

        # Hledání alfanumerického formátu (méně náchylný ke kolizím)
        for match in self.op_pattern_alphanum.finditer(text):
            start, end = match.span()
            op_text = match.group(1)
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
            # print(f"CzechOPRecognizer DEBUG (alphanum): Match '{op_text}', Score: {score}, Context: {context_found}")

            results.append(
                RecognizerResult(
                    entity_type="CZECH_OP_NUMBER",
                    start=start,
                    end=end,
                    score=score,
                    analysis_explanation=f"Found Czech OP (alphanum): {op_text}",
                    recognition_metadata={
                        RecognizerResult.RECOGNIZER_NAME_KEY: self.name,
                        RecognizerResult.RECOGNIZER_IDENTIFIER_KEY: self.id
                    }
                )
            )

        # Hledání číselného formátu
        for match in self.op_pattern_numeric.finditer(text):
            start, end = match.span()
            op_text = match.group(1)

            # Zkontrolujeme, zda tato shoda již nebyla pokryta alfanumerickým rozpoznávačem
            # nebo zda se nepřekrývá s již nalezeným alfanumerickým OP s vyšším skóre.
            is_overlapping_with_better_alphanum = False
            for res in results:
                if res.entity_type == "CZECH_OP_NUMBER" and \
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

            # Pokud jsme nenašli kontext, a jedná se o 9 číslic, skóre může být příliš nízké
            # nebo může kolidovat např. s tel. číslem. Zvážit přísnější pravidla nebo vyšší práh.

            # DEBUG:
            # print(f"CzechOPRecognizer DEBUG (numeric): Match '{op_text}', Score: {score}, Context: {context_found}, Overlap: {is_overlapping_with_better_alphanum}")

            if score > 0.5: # Prahová hodnota pro numerický OP
                results.append(
                    RecognizerResult(
                        entity_type="CZECH_OP_NUMBER",
                        start=start,
                        end=end,
                        score=score,
                        analysis_explanation=f"Found Czech OP (numeric): {op_text}",
                        recognition_metadata={
                            RecognizerResult.RECOGNIZER_NAME_KEY: self.name,
                            RecognizerResult.RECOGNIZER_IDENTIFIER_KEY: self.id
                        }
                    )
                )

        # Jednoduché odstranění duplicit, pokud by nějaké vznikly (např. dva regexy by chytily totéž)
        # A seřazení podle pozice
        final_results = []
        seen_spans = set()
        for res in sorted(results, key=lambda x: x.start):
            if (res.start, res.end) not in seen_spans:
                final_results.append(res)
                seen_spans.add((res.start, res.end))

        return final_results
