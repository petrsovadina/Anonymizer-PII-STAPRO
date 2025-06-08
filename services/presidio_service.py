import logging
from typing import Dict, List, Optional, Union
import sys
from pathlib import Path

# Přidej root directory do Python path
root_path = Path(__file__).parent.parent
sys.path.append(str(root_path))

from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
# from presidio_anonymizer.entities import OperatorConfig # Není použito
from presidio_analyzer.recognizer_result import RecognizerResult

from models.document import Document, AnonymizedDocument, DetectedEntity, AnonymizedEntity
from recognizers.registry import CzechRecognizerRegistry

# Nastavení loggeru
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class PresidioService:
    """
    Služba pro anonymizaci dokumentů pomocí Microsoft Presidio.
    """
    
    def __init__(self):
        """
        Inicializace služby Presidio.
        """
        nlp_configuration = {
            "nlp_engine_name": "spacy",
            "models": [
                {"lang_code": "en", "model_name": "en_core_web_sm"},
                {"lang_code": "cs", "model_name": "xx_ent_wiki_sm"} # Použití vícejazyčného modelu pro CS
            ]
        }
        # logger.info(f"Initializing NlpEngineProvider with configuration: {nlp_configuration}") # Odstraněno nadbytečné logování
        self.nlp_engine = NlpEngineProvider(nlp_configuration=nlp_configuration).create_engine()
        
        # Vytvoření registru rozpoznávačů s explicitní podporou jazyků
        registry = RecognizerRegistry(supported_languages=["en", "cs"])
        
        # Inicializace analyzeru s podporou pro 'en' a 'cs'
        # a s nakonfigurovaným registrem
        self.analyzer = AnalyzerEngine(
            nlp_engine=self.nlp_engine,
            registry=registry,
            supported_languages=["en", "cs"]
        )

        # Registrace specializovaných českých rozpoznávačů do nakonfigurovaného registru
        CzechRecognizerRegistry.register_czech_recognizers(registry)
        
        # Inicializace anonymizeru
        self.anonymizer = AnonymizerEngine()
        
        logger.info("Presidio service initialized with English and Czech (multilang model) support and Czech recognizers")
    
    def analyze_text(self, text: str, language: str = "cs") -> tuple[List[DetectedEntity], List[RecognizerResult]]:
        """
        Analyzuje text a detekuje entity.
        
        Args:
            text: Text k analýze
            language: Jazyk textu (výchozí: čeština)
            
        Returns:
            Tuple obsahující seznam detekovaných entit a původní výsledky analyzeru
        """
        logger.info(f"Analyzing text (length: {len(text)}) using language: {language}")
        
        # Seznam entit k detekci - vezmeme všechny, které registry podporují pro daný jazyk
        # Pokud bychom chtěli omezit, museli bychom to zde specifikovat.
        # Prozatím necháme Presidio, ať si samo vybere relevantní pro daný jazyk z registru.
        entities_to_detect = None
        
        # Analýza textu pomocí Presidio Analyzer
        # Zde předáváme language, AnalyzerEngine by měl interně vybrat správný model
        # a relevantní rozpoznávače z registru pro daný jazyk.
        results = self.analyzer.analyze(
            text=text,
            language=language,
            entities=entities_to_detect,
            allow_list=None, # Prozatím bez allow-listu
            score_threshold=0.3  # Nižší práh pro vyšší recall, můžeme upravit
        )
        
        # Konverze výsledků na DetectedEntity
        detected_entities = []
        for result in results:
            entity = DetectedEntity(
                entity_type=result.entity_type,
                start=result.start,
                end=result.end,
                score=result.score,
                text=text[result.start:result.end],
                context=self._get_context(text, result.start, result.end),
                # recognition_metadata by se dalo přidat, pokud by bylo relevantní
                metadata={}
            )
            detected_entities.append(entity)
        
        logger.info(f"Detected {len(detected_entities)} entities")
        return detected_entities, results # Vracíme i původní results pro anonymizaci
    
    def anonymize_text(
        self, 
        text: str, 
        # entities: List[DetectedEntity], # Tento parametr se zdá být nadbytečný, Anonymizer bere analyzer_results
        analyzer_results: List[RecognizerResult] # Použijeme přímo výsledky z Analyzeru
    ) -> tuple[str, List[AnonymizedEntity]]:
        """
        Anonymizuje text na základě detekovaných entit (výsledků z Analyzeru).
        
        Args:
            text: Text k anonymizaci
            analyzer_results: Původní výsledky z analyzeru
            
        Returns:
            Tuple obsahující anonymizovaný text a seznam anonymizovaných entit
        """
        logger.info(f"Anonymizing text based on {len(analyzer_results)} analyzer results")
        
        # Anonymizace textu s použitím původních výsledků analyzeru
        anonymized_result = self.anonymizer.anonymize(
            text=text,
            analyzer_results=analyzer_results
            # Operátory můžeme konfigurovat zde, pokud bychom chtěli jiné než defaultní
            # operators={"DEFAULT": OperatorConfig("replace", {"new_value": "<ANONYMIZED>"})}
        )
        
        # Vytvoření seznamu anonymizovaných entit z anonymized_result.items
        anonymized_entities = []
        # Potřebujeme původní detekované entity pro vytvoření AnonymizedEntity
        # To je trochu nešikovné, pokud bychom neměli původní DetectedEntity.
        # Prozatím předpokládáme, že si je volající podržel, nebo je zrekonstruujeme.
        # Zde by bylo lepší mít původní DetectedEntity.
        # Pro jednoduchost nyní vytvoříme AnonymizedEntity s informacemi, které máme.

        # Získání mapování z RecognizerResult na text entity
        # Toto je složitější, protože anonymizer_result.items neobsahuje přímo původní text entity,
        # ale operátor a nový text.
        # Nejlepší by bylo, kdyby anonymize vracel i mapování na původní entity,
        # nebo kdybychom si DetectedEntity předávali.

        # Prozatímní zjednodušení:
        # Budeme iterovat přes anonymizer_result.items a snažit se vytvořit AnonymizedEntity.
        # Původní text entity budeme muset odvodit z text[item.start:item.end]
        # Původní typ entity a skóre také z analyzer_results.

        # Mapování RecognizerResult (z analyzer_results) na AnonymizerResultItem (z anonymized_result.items)
        # je založeno na pozicích start a end.

        # Vytvoříme slovník pro rychlé vyhledání RecognizerResult podle pozice
        analyzer_results_map = {(res.start, res.end): res for res in analyzer_results}

        for item in anonymized_result.items:
            original_recognizer_result = analyzer_results_map.get((item.start, item.end))
            if original_recognizer_result:
                original_entity_obj = DetectedEntity(
                    entity_type=original_recognizer_result.entity_type,
                    start=original_recognizer_result.start,
                    end=original_recognizer_result.end,
                    score=original_recognizer_result.score,
                    text=text[original_recognizer_result.start:original_recognizer_result.end],
                    context="", # Kontext bychom mohli doplnit, pokud bychom ho měli u RecognizerResult
                    metadata={}
                )
                anonymized_entity = AnonymizedEntity(
                    original_entity=original_entity_obj,
                    anonymized_text=item.text, # Toto je již anonymizovaný text
                    operator_name=item.operator,
                    metadata={}
                )
                anonymized_entities.append(anonymized_entity)
        
        logger.info(f"Text anonymized successfully")
        return anonymized_result.text, anonymized_entities
    
    def process_document(self, document: Document) -> AnonymizedDocument:
        """
        Zpracuje dokument - detekuje entity a anonymizuje text.
        
        Args:
            document: Dokument ke zpracování
            
        Returns:
            Anonymizovaný dokument
        """
        logger.info(f"Processing document: {document.id}")
        
        # Detekce entit - použití jazyka dokumentu, pokud je specifikován, jinak výchozí 'cs'
        # Prozatím předpokládáme, že jazyk je 'cs' nebo 'en' podle toho, co podporujeme.
        # Pokud by dokument měl vlastní atribut language, mohli bychom ho použít.
        # Pro tento příklad použijeme 'cs' jako výchozí, pokud není řečeno jinak.
        # V našem případě testovací skript volá analyze_text s explicitním jazykem.

        # Použijeme 'cs' jako výchozí pro process_document, pokud dokument nemá specifikovaný jazyk
        # a pokud je 'cs' podporováno.
        # V tomto bodě je PresidioService již inicializováno s podporou pro 'en' a 'cs'.
        # PresidioService by měl mít nějakou logiku pro určení jazyka, pokud není explicitně dán.
        # Prozatím, pokud Document nemá jazyk, použijeme 'cs'.
        lang_to_use = document.metadata.get("language", "cs") if document.metadata else "cs"
        if lang_to_use not in self.analyzer.supported_languages:
            logger.warning(f"Language '{lang_to_use}' not supported by analyzer, defaulting to 'en'.")
            lang_to_use = "en" # Fallback na angličtinu, pokud specifikovaný jazyk není podporován

        detected_entities, analyzer_results = self.analyze_text(document.content, language=lang_to_use)
        
        # Anonymizace textu
        anonymized_text, anonymized_entities = self.anonymize_text(
            document.content, 
            analyzer_results # Předáváme přímo výsledky z analyzeru
        )
        
        # Vytvoření anonymizovaného dokumentu
        anonymized_document = AnonymizedDocument(
            id=f"anon_{document.id}" if document.id else None,
            content=anonymized_text,
            content_type=document.content_type,
            original_document_id=document.id,
            entities=anonymized_entities,
            metadata=document.metadata,
            statistics={
                "total_entities_detected": len(detected_entities),
                "entities_by_type": self._count_entities_by_type(detected_entities),
                "processing_time_ms": 0  # Toto by mělo být měřeno reálně
            }
        )
        
        logger.info(f"Document processed successfully")
        return anonymized_document
    
    def _get_context(self, text: str, start: int, end: int, window: int = 20) -> str:
        """
        Získá kontext kolem entity.
        
        Args:
            text: Celý text
            start: Počáteční pozice entity
            end: Koncová pozice entity
            window: Velikost okna pro kontext
            
        Returns:
            Kontext kolem entity
        """
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end]
    
    def _count_entities_by_type(self, entities: List[DetectedEntity]) -> Dict[str, int]:
        """
        Spočítá entity podle typu.
        
        Args:
            entities: Seznam entit
            
        Returns:
            Slovník s počty entit podle typu
        """
        counts = {}
        for entity in entities:
            if entity.entity_type in counts:
                counts[entity.entity_type] += 1
            else:
                counts[entity.entity_type] = 1
        return counts
