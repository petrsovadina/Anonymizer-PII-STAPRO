import re
from typing import List, Optional

from presidio_analyzer import EntityRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts


class CzechMedicalFacilityRecognizer(EntityRecognizer):
    """
    Rozpoznávač pro názvy českých zdravotnických zařízení.
    
    Detekuje názvy nemocnic, klinik, zdravotních středisek a dalších zdravotnických zařízení.
    """
    
    def __init__(
        self,
        supported_language: str = "cs",
        supported_entity: str = "CZECH_MEDICAL_FACILITY",
        name: str = "Czech Medical Facility Recognizer",
        context: Optional[List[str]] = None,
    ):
        self.context = context if context else []
        
        # Klíčová slova pro detekci zdravotnických zařízení
        self.facility_keywords = [
            "nemocnice", "fakultní nemocnice", "fn ", "fn,", "klinika", "poliklinika",
            "zdravotní středisko", "zdravotnické zařízení", "léčebna", "sanatorium",
            "ordinace", "ambulance", "ústav", "centrum", "oddělení", "lékařský dům",
            "lékařské centrum", "zdravotní centrum", "rehabilitační ústav", "hospic"
        ]
        
        super().__init__(
            supported_entities=[supported_entity],
            name=name,
            supported_language=supported_language,
        )
    
    def load(self) -> None:
        """Načtení rozpoznávače."""
        pass
    
    def analyze(
        self, text: str, entities: List[str], nlp_artifacts: NlpArtifacts
    ) -> List[RecognizerResult]:
        """
        Analyzuje text a detekuje názvy zdravotnických zařízení.
        
        Args:
            text: Text k analýze
            entities: Seznam entit k detekci
            nlp_artifacts: NLP artefakty
            
        Returns:
            Seznam detekovaných entit
        """
        results = []
        
        if not self.supported_entities or not entities:
            return results
        
        if not any(entity in self.supported_entities for entity in entities):
            return results
        
        # Použití NLP artefaktů pro detekci entit
        # if not nlp_artifacts or not nlp_artifacts.entities: # Kontrola nlp_artifacts.entities zde není relevantní, pokud nepoužíváme NER
        #     return results

        # Procházení textu a hledání klíčových slov
        # Tento přístup nevyužívá nlp_artifacts.doc, čímž se vyhýbá AttributeError
        text_lower = text.lower()
        for keyword in self.facility_keywords:
            keyword_lower = keyword.lower()
            current_pos = 0
            while current_pos < len(text_lower):
                keyword_index_text = text_lower.find(keyword_lower, current_pos)
                if keyword_index_text == -1:
                    break # Klíčové slovo již v textu není

                # Hledání názvu zařízení v okolí klíčového slova
                # Kontext před klíčovým slovem (např. pro "Fakultní nemocnice")
                # a za klíčovým slovem (např. pro "nemocnice v Motole")
                # Zjednodušená extrakce: vezmeme širší okolí klíčového slova.
                # Pro přesnější vymezení by bylo potřeba pokročilejší parsování nebo využití NER, pokud je dostupné.

                # Absolutní pozice klíčového slova v původním textu
                abs_keyword_start = keyword_index_text
                abs_keyword_end = keyword_index_text + len(keyword)

                # Zkusíme extrahovat kontext kolem klíčového slova jako potenciální název
                # Toto je velmi hrubý odhad a mělo by být vylepšeno.
                # Například hledáním velkých písmen před/po, nebo využitím hranic vět, pokud by byly dostupné jinak.
                context_window_before = 50 # Kolik znaků před klíčovým slovem zahrnout
                context_window_after = 70  # Kolik znaků za klíčovým slovem zahrnout

                facility_start_in_text = max(0, abs_keyword_start - context_window_before)
                facility_end_in_text = min(len(text), abs_keyword_end + context_window_after)

                # Hrubá heuristika pro "očištění" potenciálního názvu - odstranění nadbytečných mezer/znaků na krajích.
                # A pokus o nalezení hranic pomocí velkých písmen nebo konců vět (pokud bychom je měli).
                # Prozatím použijeme pevné okno, ale s vědomím, že to není ideální.
                # Příklad: "léčebna dlouhodobě nemocných" - keyword "léčebna"
                # Příklad: "Fakultní nemocnice Motol" - keyword "Fakultní nemocnice"

                # Pro jednoduchost nyní označíme širší kontext, s tím, že skóre je nižší.
                # V praxi by bylo lepší mít sofistikovanější logiku pro určení hranic entity.

                # Pro tento příklad označíme jen samotné klíčové slovo, pokud není sofistikovanější logika.
                # Nebo jednoduchý pokus o rozšíření, pokud za klíčovým slovem následuje velké písmeno (název)

                # Zjednodušení: Označíme úsek začínající kousek před klíčovým slovem a končící kousek za ním.
                # Skutečný název může být delší nebo kratší.
                # Příklad: text = "... v zařízení Fakultní nemocnice Královské Vinohrady se léčí..."
                # keyword = "Fakultní nemocnice"
                # Chceme zachytit "Fakultní nemocnice Královské Vinohrady"

                # Jednoduchá expanze doprava, dokud nenarazíme na interpunkci nebo konec věty (simulace)
                expanded_end = abs_keyword_end
                while expanded_end < len(text) and text[expanded_end].isalnum() or text[expanded_end] in ' ':
                    expanded_end += 1

                # Hrubé vymezení entity - od začátku klíčového slova po konec souvislého textu za ním
                # nebo mírně rozšířený kontext. Prozatím vezmeme kontextové okno.
                # Toto je místo, které by vyžadovalo největší vylepšení.
                # Prozatím označíme jako entitu text v kontextovém okně kolem klíčového slova.
                # Toto je velmi zjednodušené a nepřesné.
                # Lepší by bylo hledat celé fráze (např. pomocí regexů pro každý typ zařízení)

                # Prozatímní kompromis: označíme samotné klíčové slovo, pokud je víceslovné,
                # nebo se pokusíme rozšířit, pokud je jednoslovné a následuje velké písmeno.
                final_entity_start = abs_keyword_start
                final_entity_end = abs_keyword_end

                # Pokud je klíčové slovo víceslovné (např. "fakultní nemocnice"), bereme ho celé.
                # Pokud je jednoslovné (např. "nemocnice") a za ním je velké písmeno, zkusíme rozšířit.
                if ' ' not in keyword: # Jednoslovné klíčové slovo
                    # Hledáme název za klíčovým slovem (např. "nemocnice Motol")
                    # Toto je velmi zjednodušený příklad.
                    temp_end = abs_keyword_end + 1 # Začátek potenciálního názvu
                    while temp_end < len(text) and (text[temp_end].isalnum() or text[temp_end] in ' .,-()'):
                        if text[temp_end] == '\n': break # Konec řádku
                        temp_end += 1
                    # Omezíme délku rozšíření, abychom nezachytili příliš mnoho
                    final_entity_end = min(abs_keyword_end + 50, temp_end)
                    # Ořízneme koncové nealfanumerické znaky (kromě tečky za zkratkou)
                    while final_entity_end > abs_keyword_start and not text[final_entity_end-1].isalnum() and text[final_entity_end-1] != '.':
                        final_entity_end -=1

                # Vytvoření výsledku
                # Je důležité zajistit, aby se nepřidávaly překrývající se výsledky pro stejné klíčové slovo.
                # To řešíme posunem current_pos.

                facility_text_extracted = text[final_entity_start:final_entity_end]

                result = RecognizerResult(
                    entity_type="CZECH_MEDICAL_FACILITY",
                    start=final_entity_start,
                    end=final_entity_end,
                    score=0.60,  # Nižší skóre kvůli hrubší detekci bez NLP vět
                    analysis_explanation=f"Found based on keyword: {keyword}",
                    recognition_metadata={
                        RecognizerResult.RECOGNIZER_NAME_KEY: self.name,
                        RecognizerResult.RECOGNIZER_IDENTIFIER_KEY: self.id,
                        "keyword_matched": keyword,
                        "extracted_text": facility_text_extracted
                    },
                )
                results.append(result)

                current_pos = final_entity_end # Posuneme se za právě nalezenou entitu
        
        # Odstranění duplicitních nebo plně obsažených výsledků (jednoduchá forma)
        # Pokud máme [FN Motol, 0-8] a [Motol, 3-8], chceme jen to delší.
        # Toto je zjednodušené, robustnější řešení by bylo složitější.
        unique_results = []
        results.sort(key=lambda r: (r.start, -(r.end - r.start))) # Seřadit podle startu, pak podle délky (delší první)
        
        last_added_result = None
        for res in results:
            if not last_added_result or res.start >= last_added_result.end:
                unique_results.append(res)
                last_added_result = res
            # else: pokud res.start < last_added_result.end, znamená to překryv.
            # Jelikož jsou seřazeny, delší jsou první, takže kratší obsažené přeskočíme.
            # Toto jednoduché pravidlo nemusí pokrýt všechny případy dokonale.

        return unique_results
