"""
REST API pro MedDocAI Anonymizer
Umožňuje headless použití anonymizačních služeb
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import tempfile
import os
from pathlib import Path
import sys
from typing import List, Optional
import uuid
from datetime import datetime

# Přidání root cesty pro importy
root_path = Path(__file__).parent.parent
sys.path.append(str(root_path))

from services.presidio_service import PresidioService
from services.batch_processor import BatchProcessor
from models.document import Document, DocumentType, ProcessingStatus, BatchProcessingConfig
from config.settings import ConfigManager
from config.logging_config import get_logger

# Konfigurace
config = ConfigManager.get_config()
app_logger = get_logger(config.log_dir)

# FastAPI aplikace
app = FastAPI(
    title="MedDocAI Anonymizer API",
    description="REST API pro anonymizaci citlivých dat v lékařských dokumentech",
    version="1.0.0",
    contact={
        "name": "MedDocAI Team",
        "email": "support@meddocai.com",
    }
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # V produkci omezit na konkrétní domény
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency pro získání služeb
def get_presidio_service() -> PresidioService:
    return PresidioService()

def get_batch_processor() -> BatchProcessor:
    return BatchProcessor()

@app.get("/")
async def root():
    """Základní endpoint"""
    return {
        "message": "MedDocAI Anonymizer API",
        "version": "1.0.0",
        "status": "running",
        "environment": config.environment
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test spojení se službami
        presidio = get_presidio_service()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "presidio": "operational",
                "batch_processor": "operational"
            }
        }
    except Exception as e:
        app_logger.error_logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.post("/anonymize/text")
async def anonymize_text(
    text: str,
    confidence_threshold: float = 0.7,
    anonymization_method: str = "replace",
    presidio_service: PresidioService = Depends(get_presidio_service)
):
    """
    Anonymizace textu
    
    Args:
        text: Text k anonymizaci
        confidence_threshold: Práh spolehlivosti (0.0-1.0)
        anonymization_method: Metoda anonymizace (replace, mask, redact)
    """
    try:
        app_logger.log_anonymization_start("text_input", anonymization_method)
        start_time = time.time()
        
        # Provedení anonymizace
        result = presidio_service.anonymize_text(
            text, 
            confidence_threshold=confidence_threshold,
            anonymization_method=anonymization_method
        )
        
        duration = time.time() - start_time
        entities_count = len(result.get('entities', []))
        
        app_logger.log_anonymization_complete("text_input", entities_count, duration)
        
        return {
            "success": True,
            "anonymized_text": result.get('anonymized_text', ''),
            "entities_found": result.get('entities', []),
            "processing_time": duration,
            "metadata": {
                "confidence_threshold": confidence_threshold,
                "method": anonymization_method,
                "entities_count": entities_count
            }
        }
        
    except Exception as e:
        app_logger.log_error(e, "text_anonymization")
        raise HTTPException(status_code=500, detail=f"Anonymization failed: {str(e)}")

@app.post("/anonymize/file")
async def anonymize_file(
    file: UploadFile = File(...),
    confidence_threshold: float = 0.7,
    anonymization_method: str = "replace",
    presidio_service: PresidioService = Depends(get_presidio_service)
):
    """
    Anonymizace souboru
    
    Args:
        file: Soubor k anonymizaci
        confidence_threshold: Práh spolehlivosti
        anonymization_method: Metoda anonymizace
    """
    try:
        # Kontrola velikosti souboru
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > config.security.max_upload_size_mb * 1024 * 1024:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Max size: {config.security.max_upload_size_mb}MB"
            )
        
        # Kontrola typu souboru
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in config.security.allowed_file_types:
            raise HTTPException(
                status_code=415,
                detail=f"Unsupported file type: {file_extension}"
            )
        
        app_logger.log_upload(file.filename, file_size)
        app_logger.log_anonymization_start(file.filename, anonymization_method)
        
        start_time = time.time()
        
        # Vytvoření dočasného souboru
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Vytvoření Document objektu
            document = Document(
                filename=file.filename,
                file_path=temp_file_path,
                file_type=file_extension,
                doc_type=DocumentType.TEXT if file_extension == '.txt' else DocumentType.DOCX
            )
            
            # Provedení anonymizace
            result = presidio_service.anonymize_document(
                document,
                confidence_threshold=confidence_threshold,
                anonymization_method=anonymization_method
            )
            
            duration = time.time() - start_time
            entities_count = len(result.get('entities', []))
            
            app_logger.log_anonymization_complete(file.filename, entities_count, duration)
            
            # Čtení anonymizovaného obsahu
            with open(result['output_path'], 'r', encoding='utf-8') as f:
                anonymized_content = f.read()
            
            return {
                "success": True,
                "filename": file.filename,
                "anonymized_content": anonymized_content,
                "entities_found": result.get('entities', []),
                "processing_time": duration,
                "metadata": {
                    "original_size": file_size,
                    "confidence_threshold": confidence_threshold,
                    "method": anonymization_method,
                    "entities_count": entities_count
                }
            }
            
        finally:
            # Vyčištění dočasných souborů
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            if 'output_path' in result and os.path.exists(result['output_path']):
                os.unlink(result['output_path'])
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.log_error(e, f"file_anonymization:{file.filename}")
        raise HTTPException(status_code=500, detail=f"File anonymization failed: {str(e)}")

@app.post("/batch/process")
async def batch_process(
    files: List[UploadFile] = File(...),
    confidence_threshold: float = 0.7,
    anonymization_method: str = "replace",
    batch_processor: BatchProcessor = Depends(get_batch_processor)
):
    """
    Batch zpracování více souborů
    """
    try:
        if len(files) > config.anonymization.max_batch_size:
            raise HTTPException(
                status_code=400,
                detail=f"Too many files. Max batch size: {config.anonymization.max_batch_size}"
            )
        
        # Vytvoření konfigurace pro batch
        batch_config = BatchProcessingConfig(
            confidence_threshold=confidence_threshold,
            anonymization_method=anonymization_method,
            batch_size=len(files)
        )
        
        # Příprava souborů pro zpracování
        documents = []
        temp_files = []
        
        for file in files:
            content = await file.read()
            file_extension = Path(file.filename).suffix.lower()
            
            # Kontroly
            if len(content) > config.security.max_upload_size_mb * 1024 * 1024:
                raise HTTPException(status_code=413, detail=f"File {file.filename} too large")
            
            if file_extension not in config.security.allowed_file_types:
                raise HTTPException(status_code=415, detail=f"Unsupported file type: {file_extension}")
            
            # Dočasný soubor
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                temp_file.write(content)
                temp_files.append(temp_file.name)
                
                document = Document(
                    filename=file.filename,
                    file_path=temp_file.name,
                    file_type=file_extension,
                    doc_type=DocumentType.TEXT if file_extension == '.txt' else DocumentType.DOCX
                )
                documents.append(document)
        
        try:
            # Batch zpracování
            start_time = time.time()
            results = batch_processor.process_batch(documents, batch_config)
            duration = time.time() - start_time
            
            # Příprava odpovědi
            response_data = {
                "success": True,
                "processed_files": len(results),
                "processing_time": duration,
                "results": []
            }
            
            for result in results:
                response_data["results"].append({
                    "filename": result.get('filename'),
                    "status": result.get('status'),
                    "entities_found": len(result.get('entities', [])),
                    "error": result.get('error') if result.get('status') == 'error' else None
                })
            
            return response_data
            
        finally:
            # Vyčištění dočasných souborů
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
    
    except HTTPException:
        raise
    except Exception as e:
        app_logger.log_error(e, "batch_processing")
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Statistiky použití API"""
    try:
        # Zde by bylo možné implementovat skutečné statistiky z databáze
        return {
            "total_requests": "N/A - implement database tracking",
            "total_files_processed": "N/A - implement database tracking", 
            "average_processing_time": "N/A - implement database tracking",
            "uptime": "N/A - implement uptime tracking"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host=config.host,
        port=config.port + 1,  # API na jiném portu než Streamlit
        reload=config.debug,
        log_level="info" if not config.debug else "debug"
    )
