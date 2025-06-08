from typing import List, Optional

from presidio_analyzer import EntityRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts

class CzechNameRecognizer(EntityRecognizer):
    """
    Rozpoznávač českých jmen pomocí spaCy NER.
    """

    EXPECTED_SCORE = 0.85  # Výchozí skóre pro rozpoznané entity

    def __init__(
        self,
        supported_entities: Optional[List[str]] = None,
        supported_language: str = "cs",
        **kwargs,
    ):
        self.supported_entities = supported_entities if supported_entities else ["PERSON"]
        super().__init__(
            supported_entities=self.supported_entities,
            supported_language=supported_language,
            name="Czech Name Recognizer",
            **kwargs,
        )

    def load(self) -> None:
        """
        Načtení modelu - prozatím není potřeba, spoléháme na spaCy model v NlpArtifacts.
        """
        pass

    def analyze(
        self, text: str, entities: List[str], nlp_artifacts: NlpArtifacts
    ) -> List[RecognizerResult]:
        """
        Analyzuje text a hledá české jména pomocí spaCy NER.
        """
        results = []

        # Diagnostický výpis
        # print(f"CzechNameRecognizer: nlp_artifacts received: {nlp_artifacts}")
        # if nlp_artifacts:
        # print(f"CzechNameRecognizer: nlp_artifacts attributes: {dir(nlp_artifacts)}")
        # print(f"CzechNameRecognizer: nlp_artifacts.entities: {nlp_artifacts.entities}")

        if not nlp_artifacts or not nlp_artifacts.entities:
            # print("CzechNameRecognizer: No NLP artifacts or entities found.")
            return results

        # print(f"CzechNameRecognizer: Processing {len(nlp_artifacts.entities)} entities from spaCy.")
        for entity in nlp_artifacts.entities:
            # Zkontrolujeme, zda je to Span objekt a má label_ atribut
            is_spacy_span = hasattr(entity, 'label_')

            entity_type_str = ""
            current_score = self.EXPECTED_SCORE # Výchozí skóre

            if is_spacy_span:
                entity_type_str = entity.label_ # Pro SpaCy Span použijeme label_
                # SpaCy Spans nemají jednoduché 'score', takže použijeme defaultní
            elif hasattr(entity, 'entity_type'): # Pro RecognizerResult-like objekty
                entity_type_str = entity.entity_type
                if hasattr(entity, 'score'):
                    try:
                        current_score = float(entity.score)
                    except ValueError:
                        pass # Ponecháme defaultní skóre
            else:
                # Neznámý typ entity v nlp_artifacts.entities, přeskočíme
                continue

            # Porovnáváme s "PER" (běžný SpaCy label pro osobu) nebo "PERSON"
            # Presidio interně mapuje NER tagy na své vlastní, "PERSON" je standardní.
            if entity_type_str == "PER" or entity_type_str == "PERSON":
                # Presidio očekává offsety znaků, SpaCy Span má start_char a end_char.
                # Presidio NlpArtifacts by mělo normalizovat 'start' a 'end' na char offsety.
                start_offset = entity.start_char if is_spacy_span and not hasattr(entity, 'start') else entity.start
                end_offset = entity.end_char if is_spacy_span and not hasattr(entity, 'end') else entity.end

                results.append(
                    RecognizerResult(
                        entity_type="PERSON", # Normalizujeme na Presidio typ
                        start=start_offset,
                        end=end_offset,
                        score=current_score,
                        analysis_explanation=f"Detected by NER model as {entity_type_str}",
                        recognition_metadata={
                            RecognizerResult.RECOGNIZER_NAME_KEY: self.name,
                            RecognizerResult.RECOGNIZER_IDENTIFIER_KEY: self.id
                        }
                    )
                )
        return results
