"""
Testy pro datové modely dokumentů
"""
import pytest
from document import (
    Document, AnonymizedDocument, DetectedEntity, AnonymizedEntity,
    DocumentType, ProcessingStatus
)

class TestDocumentModels:
    """Testy pro základní datové modely"""
    
    def test_document_creation(self):
        """Test vytvoření dokumentu"""
        doc = Document(
            id="test_doc",
            content="Test obsah dokumentu",
            content_type="text/plain",
            document_type=DocumentType.MEDICAL_REPORT,
            source="test",
            metadata={"author": "test"},
            status=ProcessingStatus.PENDING
        )
        
        assert doc.id == "test_doc"
        assert doc.content == "Test obsah dokumentu"
        assert doc.document_type == DocumentType.MEDICAL_REPORT
        assert doc.status == ProcessingStatus.PENDING
    
    def test_document_minimal_creation(self):
        """Test vytvoření dokumentu s minimálními parametry"""
        doc = Document(
            content="Minimální obsah",
            id=None,
            content_type="text/plain",
            document_type=None,
            source=None,
            metadata=None,
            status=ProcessingStatus.PENDING
        )
        
        assert doc.content == "Minimální obsah"
        assert doc.content_type == "text/plain"
        assert doc.status == ProcessingStatus.PENDING
    
    def test_detected_entity_creation(self):
        """Test vytvoření detekované entity"""
        entity = DetectedEntity(
            entity_type="PERSON",
            start=0,
            end=8,
            score=0.95,
            text="Jan Novák",
            context="Jan Novák byl přijat",
            metadata={"confidence": "high"}
        )
        
        assert entity.entity_type == "PERSON"
        assert entity.text == "Jan Novák"
        assert entity.score == 0.95
    
    def test_anonymized_entity_creation(self):
        """Test vytvoření anonymizované entity"""
        original_entity = DetectedEntity(
            entity_type="PERSON",
            start=0,
            end=8,
            score=0.95,
            text="Jan Novák",
            context="Jan Novák byl přijat",
            metadata={}
        )
        
        anonymized_entity = AnonymizedEntity(
            original_entity=original_entity,
            anonymized_text="<PERSON>",
            operator_name="replace",
            metadata={}
        )
        
        assert anonymized_entity.original_entity.text == "Jan Novák"
        assert anonymized_entity.anonymized_text == "<PERSON>"
        assert anonymized_entity.operator_name == "replace"
    
    def test_anonymized_document_creation(self):
        """Test vytvoření anonymizovaného dokumentu"""
        original_entity = DetectedEntity(
            entity_type="PERSON",
            start=0,
            end=8,
            score=0.95,
            text="Jan Novák",
            context="Jan Novák byl přijat",
            metadata={}
        )
        
        anonymized_entity = AnonymizedEntity(
            original_entity=original_entity,
            anonymized_text="<PERSON>",
            operator_name="replace",
            metadata={}
        )
        
        anonymized_doc = AnonymizedDocument(
            id="anon_test_doc",
            original_document_id="test_doc",
            content="<PERSON> byl přijat do nemocnice",
            content_type="text/plain",
            entities=[anonymized_entity],
            metadata={},
            statistics={"total_entities": 1}
        )
        
        assert anonymized_doc.original_document_id == "test_doc"
        assert "<PERSON>" in anonymized_doc.content
        assert len(anonymized_doc.entities) == 1
        assert anonymized_doc.statistics is not None
        assert anonymized_doc.statistics["total_entities"] == 1

class TestDocumentEnums:
    """Testy pro enum typy"""
    
    def test_document_types(self):
        """Test DocumentType enum"""
        assert DocumentType.MEDICAL_REPORT == "medical_report"
        assert DocumentType.DISCHARGE_SUMMARY == "discharge_summary"
        assert DocumentType.EPICRISIS == "epicrisis"
        assert DocumentType.LABORATORY_RESULT == "laboratory_result"
    
    def test_processing_status(self):
        """Test ProcessingStatus enum"""
        assert ProcessingStatus.PENDING == "pending"
        assert ProcessingStatus.PROCESSING == "processing"
        assert ProcessingStatus.COMPLETED == "completed"
        assert ProcessingStatus.FAILED == "failed"
        assert ProcessingStatus.VALIDATED == "validated"
