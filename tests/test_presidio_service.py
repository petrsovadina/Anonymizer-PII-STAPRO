"""
Testy pro PresidioService - hlavní anonymizační službu
"""
import pytest
import sys
from pathlib import Path

# Přidání kořenového adresáře projektu do sys.path
# /app/tests/test_presidio_service.py -> /app
root_path = Path(__file__).parent.parent
sys.path.append(str(root_path))

from services.presidio_service import PresidioService
from models.document import Document, DocumentType, ProcessingStatus


class TestPresidioService:
    """Test class pro PresidioService"""
    
    @pytest.fixture
    def presidio_service(self):
        """Fixture pro inicializaci PresidioService"""
        return PresidioService()
    
    @pytest.fixture
    def sample_document(self):
        """Fixture pro ukázkový dokument"""
        return Document(
            id="test_doc_1",
            content="Jan Novák, rodné číslo 760506/1234, email: jan.novak@email.com",
            content_type="text/plain",
            document_type=DocumentType.MEDICAL_REPORT,
            source="test",
            metadata={},
            status=ProcessingStatus.PENDING
        )
    
    def test_service_initialization(self, presidio_service):
        """Test inicializace služby"""
        assert presidio_service is not None
        assert presidio_service.analyzer is not None
        assert presidio_service.anonymizer is not None
    
    def test_analyze_text_czech(self, presidio_service):
        """Test analýzy českého textu"""
        text = "Jan Novák, rodné číslo 760506/1234"
        entities, results = presidio_service.analyze_text(text, "cs")
        assert len(entities) > 0
        # Očekáváme detekci jména a rodného čísla
        entity_types = [entity.entity_type for entity in entities]
        assert "PERSON" in entity_types
    
    def test_analyze_text_english(self, presidio_service):
        """Test analýzy anglického textu"""
        text = "John Doe, email: john.doe@email.com"
        entities, results = presidio_service.analyze_text(text, "en")
        assert len(entities) > 0
        entity_types = [entity.entity_type for entity in entities]
        assert "PERSON" in entity_types
        assert "EMAIL_ADDRESS" in entity_types
    
    def test_process_document(self, presidio_service, sample_document):
        """Test zpracování celého dokumentu"""
        anonymized_doc = presidio_service.process_document(sample_document)
        
        assert anonymized_doc is not None
        assert anonymized_doc.content != sample_document.content
        assert anonymized_doc.original_document_id == sample_document.id
        assert len(anonymized_doc.entities) > 0
        assert anonymized_doc.statistics is not None
    
    def test_anonymization_preserves_structure(self, presidio_service):
        """Test, že anonymizace zachovává strukturu textu"""
        text = "Pacient Jan Novák byl přijat 15.6.2023."
        document = Document(
            id="test_structure",
            content=text,
            content_type="text/plain",
            document_type=DocumentType.MEDICAL_REPORT,
            source="test",
            metadata={},
            status=ProcessingStatus.PENDING
        )
        
        anonymized_doc = presidio_service.process_document(document)
        
        # Text by měl obsahovat anonymizované entity ale zachovat strukturu
        assert "byl přijat" in anonymized_doc.content
        assert "Jan Novák" not in anonymized_doc.content
