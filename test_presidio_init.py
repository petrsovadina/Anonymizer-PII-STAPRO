import sys
from pathlib import Path

try:
    print("Pokus o import PresidioService...")
    from services.presidio_service import PresidioService
    print("Import PresidioService úspěšný.")

    print("Pokus o inicializaci PresidioService...")
    service = PresidioService()
    print("Inicializace PresidioService úspěšná.")

    print(f"Typ použitého NLP enginu: {type(service.analyzer.nlp_engine)}")

    if service.analyzer.nlp_engine and hasattr(service.analyzer.nlp_engine, 'nlp'):
        print(f"Načtené jazyky v NLP enginu: {list(service.analyzer.nlp_engine.nlp.keys())}")
        if 'en' in service.analyzer.nlp_engine.nlp:
            print(f"Model pro 'en' je načten: {type(service.analyzer.nlp_engine.nlp['en'])}")
        else:
            print("Anglický model NENÍ načten v NLP enginu.")

        if 'cs' in service.analyzer.nlp_engine.nlp:
            print(f"Model pro 'cs' je načten: {type(service.analyzer.nlp_engine.nlp['cs'])}")
        else:
            print("Český model (nebo fallback) NENÍ načten v NLP enginu.")
    else:
        print("NLP engine nebo jeho vnitřní nlp objekt není správně inicializován.")

    print(f"Podporované jazyky v analyzeru: {service.analyzer.supported_languages}")
    print(f"Podporované jazyky v registru rozpoznávačů: {service.analyzer.registry.supported_languages}")

    print("\n--- Test detekce emailu ---")
    test_text_email = "Napište nám email na info@example.com nebo na podpora.uzivatelu@example.co.cz."
    print(f"Testovací text pro email: '{test_text_email}'")
    results_email, _ = service.analyze_text(test_text_email, language="cs")
    print(f"Nalezené entity ({len(results_email)}):")
    email_detected = False
    for entity in results_email:
        print(f"- Typ: {entity.entity_type}, Text: '{test_text_email[entity.start:entity.end]}', Skóre: {entity.score:.2f}")
        if entity.entity_type == "EMAIL_ADDRESS":
            email_detected = True
    if email_detected:
        print("  EMAIL_ADDRESS ÚSPĚŠNĚ DETEKOVÁN.")
    else:
        print("  EMAIL_ADDRESS NEBYL DETEKOVÁN.")

    print("\n--- Test detekce českých bankovních účtů ---")
    test_text_bank = "Platbu zašlete na účet číslo 123456-1234567890/0800 nebo na 9876543210/0100. Další účet je 12345/5500."
    print(f"Testovací text pro bankovní účty: '{test_text_bank}'")
    results_bank, _ = service.analyze_text(test_text_bank, language="cs")
    print(f"Nalezené entity ({len(results_bank)}):")
    bank_account_detected = False
    for entity in results_bank:
        print(f"- Typ: {entity.entity_type}, Text: '{test_text_bank[entity.start:entity.end]}', Skóre: {entity.score:.2f}")
        if entity.entity_type == "CZECH_BANK_ACCOUNT_NUMBER":
            bank_account_detected = True
            # Výpis metadat pro ověření správnosti parsování
            if hasattr(entity, 'recognition_metadata') and entity.recognition_metadata:
                print(f"  Metadata: Prefix='{entity.recognition_metadata.get('prefix', '')}', "
                      f"Main='{entity.recognition_metadata.get('account_number_main', '')}', "
                      f"BankCode='{entity.recognition_metadata.get('bank_code', '')}'")
    if bank_account_detected:
        print("  CZECH_BANK_ACCOUNT_NUMBER ÚSPĚŠNĚ DETEKOVÁN.")
    else:
        print("  CZECH_BANK_ACCOUNT_NUMBER NEBYL DETEKOVÁN.")


except ImportError as e:
    print(f"Chyba při importu: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Chyba při inicializaci nebo testu: {e}")
    sys.exit(1)

print("\nTest dokončen úspěšně.")
