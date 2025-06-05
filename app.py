import streamlit as st
import pandas as pd
import os
import json
import time
from pathlib import Path

# Import služeb z projektu
from presidio_service import PresidioService
from document import Document, DocumentType, ProcessingStatus

# Konfigurace stránky
st.set_page_config(
    page_title="MedDocAI Anonymizer",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inicializace služeb
@st.cache_resource
def load_presidio_service():
    try:
        return PresidioService()
    except Exception as e:
        st.error(f"Chyba při načítání Presidio služby: {e}")
        return None

# Funkce pro anonymizaci textu
def anonymize_text(text, language="en"):
    """Anonymizuje zadaný text."""
    presidio_service = load_presidio_service()
    if presidio_service is None:
        return None
    
    try:
        # Vytvoření dokumentu podle skutečné struktury
        document = Document(
            id="streamlit_input",
            content=text,
            content_type="text/plain",
            document_type=DocumentType.MEDICAL_REPORT,
            source="streamlit",
            metadata={},
            status=ProcessingStatus.PENDING
        )
        
        start_time = time.time()
        anonymized_document = presidio_service.process_document(document)
        processing_time = (time.time() - start_time) * 1000  # v ms
        
        return {
            "anonymized_text": anonymized_document.content,
            "processing_time_ms": processing_time,
            "entities": [
                {
                    "entity_type": entity.original_entity.entity_type,
                    "text": entity.original_entity.text,
                    "anonymized_text": entity.anonymized_text,
                    "score": entity.original_entity.score,
                    "start": entity.original_entity.start,
                    "end": entity.original_entity.end
                }
                for entity in anonymized_document.entities
            ] if anonymized_document.entities else []
        }
    except Exception as e:
        st.error(f"Chyba při anonymizaci: {e}")
        return None

# Funkce pro zobrazení detekovaných entit
def display_entities(entities):
    if not entities:
        st.info("Nebyly nalezeny žádné entity k anonymizaci.")
        return
    
    st.subheader("Detekované a anonymizované entity")
    
    entity_data = []
    for entity in entities:
        entity_data.append({
            "Typ entity": entity["entity_type"],
            "Původní text": entity["text"],
            "Anonymizovaný text": entity["anonymized_text"],
            "Skóre": f"{entity['score']:.2f}",
            "Pozice": f"{entity['start']}-{entity['end']}"
        })
    
    st.dataframe(pd.DataFrame(entity_data), use_container_width=True)

# Hlavní aplikace
def main():
    # Sidebar
    st.sidebar.title("🔒 MedDocAI Anonymizer")
    st.sidebar.markdown("---")
    
    app_mode = st.sidebar.selectbox(
        "Vyberte režim",
        ["Anonymizace textu", "O aplikaci"]
    )
    
    # Nastavení
    with st.sidebar.expander("⚙️ Nastavení"):
        language = st.selectbox("Jazyk", ["en", "cs"], index=0, 
                               help="cs - čeština (experimentální), en - angličtina")
        show_entities = st.checkbox("Zobrazit detekované entity", value=True)
    
    # Anonymizace textu
    if app_mode == "Anonymizace textu":
        st.title("🏥 Anonymizace zdravotnického textu")
        st.markdown("Zadejte text, který chcete anonymizovat:")
        
        # Výběr ukázkového textu
        sample_texts = {
            "České ukázka": "Pacient Jan Novák, rodné číslo 760506/1234, byl přijat do Fakultní nemocnice v Motole s diagnózou J45.0 (Astma). Kontakt: jan.novak@email.com, telefon 606 123 456.",
            "Anglická ukázka": "Patient John Doe, SSN 123-45-6789, was admitted to General Hospital with diagnosis of diabetes. Contact: john.doe@email.com, phone +1-555-123-4567.",
            "Vlastní text": ""
        }
        
        selected_sample = st.selectbox("Vyberte ukázkový text nebo zadejte vlastní:", list(sample_texts.keys()))
        
        if selected_sample == "Vlastní text":
            text_input = st.text_area("Vstupní text", height=200, placeholder="Zadejte text k anonymizaci...")
        else:
            text_input = st.text_area("Vstupní text", value=sample_texts[selected_sample], height=200)
        
        if st.button("🔒 Anonymizovat", type="primary", disabled=not text_input.strip()):
            with st.spinner("Probíhá anonymizace..."):
                result = anonymize_text(text_input, language)
                
                if result:
                    st.success("Anonymizace byla úspěšně dokončena!")
                    
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.subheader("📄 Anonymizovaný text")
                        st.text_area("Výstup", result["anonymized_text"], height=200, key="output")
                    
                    with col2:
                        st.metric("⏱️ Doba zpracování", f"{result['processing_time_ms']:.1f} ms")
                        st.metric("🔍 Nalezené entity", len(result["entities"]))
                    
                    # Tlačítko pro stažení
                    st.download_button(
                        label="📥 Stáhnout anonymizovaný text",
                        data=result["anonymized_text"],
                        file_name="anonymized_text.txt",
                        mime="text/plain"
                    )
                    
                    if show_entities:
                        display_entities(result["entities"])
                else:
                    st.error("Anonymizace selhala. Zkontrolujte zadaný text a zkuste to znovu.")
    
    # O aplikaci
    else:
        st.title("ℹ️ O aplikaci MedDocAI Anonymizer")
        
        st.markdown("""
        ## 🔒 MedDocAI Anonymizer
        
        **Specializovaný nástroj pro anonymizaci zdravotnické dokumentace** vyvinutý pro ochranu osobních údajů pacientů v souladu s GDPR.
        
        ### ✨ Klíčové funkce
        
        - 🔍 **Automatická detekce citlivých údajů** v zdravotnických textech
        - 🇨🇿 **Podpora českého jazyka** s rozpoznáváním rodných čísel, adres a zdravotnické terminologie
        - 🌐 **Mezinárodní podpora** pro anglické texty
        - ⚡ **Rychlé zpracování** s detailními statistikami
        - 🔒 **Bezpečná anonymizace** zachovávající klinickou relevanci
        
        ### 🎯 Rozpoznávané entity
        
        #### Standardní entity
        - 👤 **PERSON** - Jména osob
        - 📧 **EMAIL_ADDRESS** - E-mailové adresy  
        - 📞 **PHONE_NUMBER** - Telefonní čísla
        - 📍 **LOCATION** - Lokace a adresy
        - 📅 **DATE_TIME** - Datumy a časy
        
        #### České specializované entity
        - 🆔 **CZECH_BIRTH_NUMBER** - České rodné číslo
        - 🏥 **CZECH_MEDICAL_FACILITY** - Zdravotnická zařízení
        - 📋 **CZECH_DIAGNOSIS_CODE** - Kódy diagnóz (MKN-10)
        - 🏠 **CZECH_ADDRESS** - České adresy
        
        ### 🚀 Jak začít
        
        1. Vyberte **"Anonymizace textu"** v menu
        2. Zadejte nebo vyberte ukázkový text
        3. Zvolte jazyk (doporučeno: angličtina pro lepší výsledky)
        4. Klikněte na **"Anonymizovat"**
        5. Stáhněte anonymizovaný výsledek
        
        ### ⚠️ Důležité poznámky
        
        - **Testovací verze**: Aplikace je v testovací fázi
        - **Angličtina**: Pro nejlepší výsledky používejte anglické texty
        - **Čeština**: Česká podpora je experimentální
        - **Offline**: Všechna data se zpracovávají lokálně
        
        ### 📊 Technické informace
        
        - **Engine**: Microsoft Presidio
        - **NLP**: spaCy s vlastními českými rozpoznávači
        - **Bezpečnost**: Lokální zpracování bez odesílání dat
        - **Výkon**: Optimalizováno pro texty do 10 000 znaků
        
        ### 🆘 Podpora
        
        Pro technickou podporu a dotazy kontaktujte vývojový tým.
        
        ---
        
        **© 2025 MedDocAI Anonymizer - Ochrana dat ve zdravotnictví**
        """)

if __name__ == "__main__":
    main()
