"""
Integrační testy pro celý anonymizační systém
"""
import pytest
from presidio_service import PresidioService
from document import Document, DocumentType, ProcessingStatus

class TestIntegration:
    """Integrační testy celého systému"""
    
    @pytest.fixture
    def presidio_service(self):
        """Fixture pro PresidioService"""
        return PresidioService()
    
    def test_end_to_end_czech_anonymization(self, presidio_service):
        """Test kompletní anonymizace českého textu"""
        # Vstupní dokument s českými entitami
        input_text = """
        Pacient: Jan Novák
        Rodné číslo: 760506/1234
        Email: jan.novak@email.com
        Telefon: +420 606 123 456
        Adresa: Václavské náměstí 1, Praha 1
        Diagnóza: J45.0 - Asthma bronchiale
        Zdravotnické zařízení: Fakultní nemocnice v Motole
        """
        
        document = Document(
            id="czech_integration_test",
            content=input_text,
            content_type="text/plain",
            document_type=DocumentType.MEDICAL_REPORT,
            source="integration_test",
            metadata={"language": "cs"},
            status=ProcessingStatus.PENDING
        )
        
        # Zpracování dokumentu
        anonymized_doc = presidio_service.process_document(document)
        
        # Ověření výsledků
        assert anonymized_doc is not None
        assert anonymized_doc.content != input_text
        assert anonymized_doc.original_document_id == "czech_integration_test"
        
        # Ověření, že citlivé údaje byly anonymizovány
        assert "Jan Novák" not in anonymized_doc.content
        assert "jan.novak@email.com" not in anonymized_doc.content
        assert "+420 606 123 456" not in anonymized_doc.content
        
        # Ověření, že struktura zůstala zachována
        assert "Pacient:" in anonymized_doc.content
        assert "Rodné číslo:" in anonymized_doc.content
        assert "Email:" in anonymized_doc.content
        assert "Diagnóza:" in anonymized_doc.content
        
        # Ověření statistik
        assert anonymized_doc.statistics is not None
        assert anonymized_doc.statistics["total_entities_detected"] > 0
        assert len(anonymized_doc.entities) > 0
    
    def test_end_to_end_english_anonymization(self, presidio_service):
        """Test kompletní anonymizace anglického textu"""
        input_text = """
        Patient: John Doe
        SSN: 123-45-6789
        Email: john.doe@hospital.com
        Phone: +1-555-123-4567
        Address: 123 Main Street, New York, NY 10001
        Date of Birth: 1985-06-15
        Insurance: Blue Cross Blue Shield
        """
        
        document = Document(
            id="english_integration_test",
            content=input_text,
            content_type="text/plain",
            document_type=DocumentType.MEDICAL_REPORT,
            source="integration_test",
            metadata={"language": "en"},
            status=ProcessingStatus.PENDING
        )
        
        # Zpracování dokumentu
        anonymized_doc = presidio_service.process_document(document)
        
        # Ověření výsledků
        assert anonymized_doc is not None
        assert anonymized_doc.content != input_text
        
        # Ověření anonymizace citlivých údajů
        assert "John Doe" not in anonymized_doc.content
        assert "123-45-6789" not in anonymized_doc.content
        assert "john.doe@hospital.com" not in anonymized_doc.content
        assert "+1-555-123-4567" not in anonymized_doc.content
        
        # Ověření zachování struktury
        assert "Patient:" in anonymized_doc.content
        assert "SSN:" in anonymized_doc.content
        assert "Email:" in anonymized_doc.content
        assert "Phone:" in anonymized_doc.content
    
    def test_mixed_language_document(self, presidio_service):
        """Test dokumentu se smíšenými jazyky"""
        input_text = """
        Patient Information / Informace o pacientovi:
        Name / Jméno: Jane Smith
        Czech Birth Number / České rodné číslo: 856215/1234
        Email: jane.smith@example.com
        US Phone: +1-555-987-6543
        Czech Phone: +420 777 888 999
        """
        
        document = Document(
            id="mixed_language_test",
            content=input_text,
            content_type="text/plain",
            document_type=DocumentType.MEDICAL_REPORT,
            source="integration_test",
            metadata={"language": "mixed"},
            status=ProcessingStatus.PENDING
        )
        
        anonymized_doc = presidio_service.process_document(document)
        
        # Ověření anonymizace
        assert "Jane Smith" not in anonymized_doc.content
        assert "856215/1234" not in anonymized_doc.content
        assert "jane.smith@example.com" not in anonymized_doc.content
        
        # Ověření zachování struktury
        assert "Patient Information" in anonymized_doc.content
        assert "Informace o pacientovi" in anonymized_doc.content
    
    def test_performance_benchmark(self, presidio_service):
        """Test výkonu anonymizace"""
        import time
        
        # Střední velikost dokumentu
        input_text = """
        Zdravotnická zpráva
        Pacient: Martin Svoboda
        Rodné číslo: 801122/3456
        Email: martin.svoboda@email.cz
        Telefon: 608 987 654
        
        Anamnéza: Pacient uvádí bolesti hlavy trvající 3 dny.
        Předchozí onemocnění: Hypertenze, diabetes mellitus typ 2.
        Současná medikace: Metformin 850mg 2x denně.
        
        Objektivní nález:
        TK: 140/90 mmHg
        Puls: 82/min
        Tělesná teplota: 36.8°C
        
        Diagnóza: G44.2 - Tenzní bolest hlavy
        Doporučení: Klid, analgetika dle potřeby
        Kontrola za 1 týden.
        
        Vyšetřující lékař: MUDr. Petr Novotný
        Datum: 15.6.2023
        Zdravotnické zařízení: Poliklinika Karlovy Vary
        """ * 3  # Trojnásobek pro test výkonu
        
        document = Document(
            id="performance_test",
            content=input_text,
            content_type="text/plain",
            document_type=DocumentType.MEDICAL_REPORT,
            source="performance_test",
            metadata={},
            status=ProcessingStatus.PENDING
        )
        
        start_time = time.time()
        anonymized_doc = presidio_service.process_document(document)
        end_time = time.time()
        
        processing_time = (end_time - start_time) * 1000  # v ms
        
        # Ověření výsledků
        assert anonymized_doc is not None
        assert len(anonymized_doc.entities) > 0
        
        # Performance assertion - mělo by být rychlejší než 2 sekundy
        assert processing_time < 2000, f"Zpracování trvalo {processing_time:.1f}ms"
        
        print(f"Performance: Zpracování {len(input_text)} znaků trvalo {processing_time:.1f}ms")
