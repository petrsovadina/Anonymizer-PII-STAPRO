import re
from typing import List, Optional

from presidio_analyzer import EntityRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts

class CzechAddressRecognizer(EntityRecognizer):
    """
    Rozpoznávač pro české adresy.
    
    Detekuje adresy v českém formátu, včetně ulic, čísel popisných/orientačních, měst a PSČ.
    Snaží se skládat jednotlivé části do kompletnější adresy.
    """

    # Definice regulárních výrazů
    # PSČ: \b\d{3}\s?\d{2}\b (povoluje mezeru uprostřed)
    ZIP_CODE_REGEX = r"\b(\d{3}\s?\d{2})\b"

    # Ulice s číslem: Zahrnuje běžné názvy ulic, tečky, pomlčky, mezery v názvu ulice.
    # Číslo popisné/orientační: \d+[a-zA-Z]?(\s?/\s?\d+[a-zA-Z]?)?
    #   - \d+[a-zA-Z]? : číslo popisné, může končit písmenem (např. 123a)
    #   - (/\d+[a-zA-Z]?)? : volitelné číslo orientační za lomítkem, také může končit písmenem (např. /4b)
    #   - \s? mezi čísly a lomítkem povoluje mezery
    # Ulice může obsahovat více slov, tečky, pomlčky.
    # ([a-zA-ZáčďéěíňóřšťúůýžÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ\s.-]+?) : Název ulice (non-greedy)
    # \s+ : Mezera před číslem
    # (\d+[a-zA-Z]?(\s?/\s?\d+[a-zA-Z]?)?) : Číslo popisné/orientační
    STREET_WITH_NUMBER_REGEX = r"([a-zA-ZáčďéěíňóřšťúůýžÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ\s.-]+?)\s+(\d+[a-zA-Z]?(\s?/\s?\d+[a-zA-Z]?)?)\b"
    
    # Město: Začíná velkým písmenem, může mít více částí (např. Nové Město na Moravě)
    # nebo být jednoduché. Může obsahovat i číslovky (např. Albrechtice I)
    # ([A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-zA-Záčďéěíňóřšťúůýž\s.-]*(?:\s+[IVXLCDM]+)?)\b
    # Tento regex je stále zjednodušený a může vyžadovat další zpřesnění.
    # Prozatím se zaměříme na kombinaci s PSČ a ulicí.
    CITY_REGEX = r"\b([A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-zA-Záčďéěíňóřšťúůýž\s.-]*(?:\s+[IVXLCDM]+)?)\b"

    # Kontextová slova pro zvýšení spolehlivosti
    CONTEXT_WORDS = [
        "adresa", "bydliště", "sídlo", "ulice", "ul.", "náměstí", "nám.",
        "třída", "tř.", "nábřeží", "sídliště", "obec", "město", "psč",
        "doručovací adresa", "fakturační adresa"
    ]

    def __init__(
        self,
        supported_entities: Optional[List[str]] = None,
        supported_language: str = "cs",
        **kwargs,
    ):
        self.supported_entities = supported_entities if supported_entities else ["CZECH_ADDRESS"]
        super().__init__(
            supported_entities=self.supported_entities,
            supported_language=supported_language,
            name="Czech Address Recognizer v2", # Změna názvu pro odlišení
            context=self.CONTEXT_WORDS,
            **kwargs,
        )
        
        # Kompilace regexů
        self.zip_code_pattern = re.compile(self.ZIP_CODE_REGEX)
        self.street_with_number_pattern = re.compile(self.STREET_WITH_NUMBER_REGEX)
        self.city_pattern = re.compile(self.CITY_REGEX) # Prozatím méně využíváno samostatně

    def load(self) -> None:
        """Načtení modelu - není potřeba pro tento regex-based recognizer."""
        pass

    def analyze(
        self, text: str, entities: List[str], nlp_artifacts: NlpArtifacts
    ) -> List[RecognizerResult]:
        results = []

        # Hledání PSČ jako první krok
        for zip_match in self.zip_code_pattern.finditer(text):
            zip_code_text = zip_match.group(1)
            zip_start, zip_end = zip_match.span()
            
            # Hledání ulice s číslem v blízkosti PSČ (do 50 znaků před)
            # a města (mezi ulicí a PSČ, nebo těsně před PSČ)
            search_before_zip_start = max(0, zip_start - 100) # Okno pro ulici a město
            text_before_zip = text[search_before_zip_start:zip_start].strip()

            street_match = None
            # Hledáme ulici s číslem od konce text_before_zip (blíže k PSČ)
            # Iterujeme přes možné shody ulice, abychom našli tu nejblíže k PSČ
            best_street_match_for_zip = None
            for s_match in self.street_with_number_pattern.finditer(text_before_zip):
                if best_street_match_for_zip is None or s_match.start() > best_street_match_for_zip.start():
                    best_street_match_for_zip = s_match
            
            if best_street_match_for_zip:
                street_text = best_street_match_for_zip.group(0) # Celá ulice s číslem
                street_name = best_street_match_for_zip.group(1).strip()
                house_number = best_street_match_for_zip.group(2).strip()

                # Relativní start a konec ulice vůči text_before_zip
                street_start_relative = best_street_match_for_zip.start()
                street_end_relative = best_street_match_for_zip.end()

                # Absolutní start a konec ulice v původním textu
                street_start_absolute = search_before_zip_start + street_start_relative
                street_end_absolute = search_before_zip_start + street_end_relative

                # Město by mělo být mezi koncem ulice a začátkem PSČ
                # nebo pokud je ulice hned u PSČ, tak před ulicí.
                potential_city_text = text_before_zip[street_end_relative:].strip()
                if not potential_city_text and street_start_relative > 0: # Pokud je ulice na konci a něco je před ní
                    potential_city_text = text_before_zip[:street_start_relative].strip()

                city_text = None
                city_matches = list(self.city_pattern.finditer(potential_city_text))
                if city_matches:
                    # Preferujeme shodu města, která je blíže k PSČ (tj. na konci potential_city_text)
                    # nebo pokud je potential_city_text celé město.
                    # Toto je zjednodušení, robustnější by bylo parsování s ohledem na strukturu.
                    city_text = city_matches[-1].group(1).strip()

                # Sestavení adresy
                address_start = street_start_absolute
                address_end = zip_end
                score = 0.6 # Základní skóre pro ulici + PSČ
                if city_text:
                    score += 0.2 # Bonus za město

                # Kontrola kontextových slov
                context_score = self.get_context_based_score(text, address_start, address_end)
                final_score = min(1.0, score + context_score)

                results.append(
                    RecognizerResult(
                        entity_type="CZECH_ADDRESS",
                        start=address_start,
                        end=address_end,
                        score=final_score,
                        analysis_explanation=f"Found address: {street_text}, {city_text or '[město?]'}, {zip_code_text}",
                        recognition_metadata={
                            "street": street_name,
                            "house_number": house_number,
                            "city": city_text,
                            "zip_code": zip_code_text,
                            RecognizerResult.RECOGNIZER_NAME_KEY: self.name,
                            RecognizerResult.RECOGNIZER_IDENTIFIER_KEY: self.id
                        }
                    )
                )
                continue # Již jsme našli adresu spojenou s tímto PSČ

        # Hledání ulice s číslem samostatně (s nižším skóre, pokud není PSČ)
        for street_match in self.street_with_number_pattern.finditer(text):
            # Zkontrolujeme, zda tato shoda již nebyla pokryta v rámci adresy s PSČ
            already_covered = False
            for res in results:
                if street_match.start() >= res.start and street_match.end() <= res.end:
                    already_covered = True
                    break
            if already_covered:
                continue

            street_text = street_match.group(0)
            street_name = street_match.group(1).strip()
            house_number = street_match.group(2).strip()
            
            current_score = 0.4 # Nižší skóre pro samostatnou ulici s číslem
            context_score = self.get_context_based_score(text, street_match.start(), street_match.end())
            final_score = min(1.0, current_score + context_score)

            if final_score > 0.5: # Prahová hodnota pro samostatnou ulici
                results.append(
                    RecognizerResult(
                        entity_type="CZECH_ADDRESS", # Nebo by to mohla být "STREET_ADDRESS"
                        start=street_match.start(),
                        end=street_match.end(),
                        score=final_score,
                        analysis_explanation=f"Found street: {street_text}",
                        recognition_metadata={
                            "street": street_name,
                            "house_number": house_number,
                            RecognizerResult.RECOGNIZER_NAME_KEY: self.name,
                            RecognizerResult.RECOGNIZER_IDENTIFIER_KEY: self.id
                        }
                    )
                )
        
        # Odstranění překrývajících se výsledků s nižším skóre
        # (jednoduchá implementace, může být vylepšena)
        final_results = []
        for res1 in sorted(results, key=lambda x: x.score, reverse=True):
            is_overlapping = False
            for res2 in final_results:
                if res1.start < res2.end and res1.end > res2.start: # Overlap
                    is_overlapping = True
                    break
            if not is_overlapping:
                final_results.append(res1)
                
        return final_results

    def get_context_based_score(self, text: str, match_start: int, match_end: int, window: int = 50) -> float:
        """
        Upraví skóre na základě přítomnosti kontextových slov kolem nalezené entity.
        """
        text_before = text[max(0, match_start - window):match_start].lower()
        text_after = text[match_end:min(len(text), match_end + window)].lower()
        
        for word in self.context:
            if word.lower() in text_before or word.lower() in text_after:
                return 0.25 # Bonus za kontext
        return 0.0
