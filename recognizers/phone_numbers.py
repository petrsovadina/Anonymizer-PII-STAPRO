import re
from typing import List, Optional

from presidio_analyzer import EntityRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts

class CzechPhoneNumberRecognizer(EntityRecognizer):
    """
    Rozpoznávač českých telefonních čísel.
    """

    # Regex pro česká telefonní čísla:
    # 1. (?:\+420\s?)? : Volitelná předvolba +420 následovaná volitelnou mezerou.
    # 2. (?: ... | ...) : Skupina pro dvě hlavní varianty formátu:
    #    a. \d{3}\s?\d{3}\s?\d{3} : Devět číslic rozdělených do trojic volitelnými mezerami.
    #    b. \d{9} : Devět číslic bez mezer.
    # 3. \b : Hranice slova na konci, aby se zabránilo částečným shodám.
    PHONE_REGEX = r"(?:\+420\s?)?(?:\d{3}\s?\d{3}\s?\d{3}|\d{9})\b"

    # Kontextová slova
    CONTEXT_WORDS = [
        "tel", "telefon", "mobil", "tel.", "číslo", "volejte", "kontakt"
    ]

    DEFAULT_SCORE = 0.7  # Základní skóre pro nalezené telefonní číslo
    CONTEXT_SCORE_BOOST = 0.2 # Zvýšení skóre při nalezení kontextového slova

    def __init__(
        self,
        supported_entities: Optional[List[str]] = None,
        supported_language: str = "cs",
        **kwargs,
    ):
        self.supported_entities = supported_entities if supported_entities else ["CZECH_PHONE_NUMBER"]
        super().__init__(
            supported_entities=self.supported_entities,
            supported_language=supported_language,
            name="Czech Phone Number Recognizer",
            context=self.CONTEXT_WORDS, # Přidání kontextových slov do Presidio
            **kwargs,
        )
        self.phone_pattern = re.compile(self.PHONE_REGEX)

    def load(self) -> None:
        """Načtení modelu - není potřeba pro tento regex-based recognizer."""
        pass

    def analyze(
        self, text: str, entities: List[str], nlp_artifacts: NlpArtifacts
    ) -> List[RecognizerResult]:
        results = []
        for match in self.phone_pattern.finditer(text):
            start, end = match.span()
            current_text = match.group(0)

            # Výpočet skóre na základě kontextu
            score = self.DEFAULT_SCORE
            # Použijeme zděděnou metodu pro kontrolu kontextu, pokud je dostupná,
            # nebo implementujeme vlastní jednoduchou logiku.
            # Presidio EntityRecognizer má atribut self.context a metody pro jeho využití.
            # Pro jednoduchost zde ukážu přímou kontrolu.

            text_before = text[max(0, start - 30):start].lower() # Okno 30 znaků před
            text_after = text[end:min(len(text), end + 10)].lower() # Okno 10 znaků za

            for word in self.context: # self.context je definován v EntityRecognizer
                if word.lower() in text_before or word.lower() in text_after:
                    score = min(1.0, score + self.CONTEXT_SCORE_BOOST)
                    break

            # Normalizace telefonního čísla (odstranění mezer, přidání +420 pokud chybí)
            normalized_phone = current_text.replace(" ", "")
            if not normalized_phone.startswith("+420") and len(normalized_phone) == 9:
                normalized_phone = "+420" + normalized_phone
            elif normalized_phone.startswith("+420") and len(normalized_phone) == 13: # +420XXXXXXXXX
                pass # již je v pořádku
            # Jiné případy můžeme ignorovat nebo jim dát nižší skóre, pokud nejsou validní

            # Základní validace délky po normalizaci
            if not (len(normalized_phone) == 13 and normalized_phone.startswith("+420")) and \
               not (len(normalized_phone) == 9 and not normalized_phone.startswith("+")):
                # Pokud po normalizaci číslo neodpovídá očekávané délce, můžeme ho přeskočit
                # nebo dát velmi nízké skóre. Prozatím přeskočíme.
                # Toto je pro případ, že by regex zachytil něco nechtěného,
                # i když \b by tomu měl bránit.
                continue

            results.append(
                RecognizerResult(
                    entity_type="CZECH_PHONE_NUMBER",
                    start=start,
                    end=end,
                    score=score,
                    analysis_explanation=f"Found Czech phone number: {current_text}",
                    recognition_metadata={
                        "normalized_value": normalized_phone,
                        RecognizerResult.RECOGNIZER_NAME_KEY: self.name,
                        RecognizerResult.RECOGNIZER_IDENTIFIER_KEY: self.id
                    }
                )
            )
        return results
