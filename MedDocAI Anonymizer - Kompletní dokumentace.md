# MedDocAI Anonymizer - Kompletní dokumentace

## Obsah balíčku

Tento balíček obsahuje kompletní dokumentaci pro vývoj a implementaci MedDocAI Anonymizeru - specializovaného nástroje pro anonymizaci zdravotnické dokumentace v českém prostředí. Dokumentace je strukturována do následujících částí:

1. **[Produktová specifikace](produktova_specifikace.md)** - Detailní popis produktu, jeho funkcí, požadavků a omezení
2. **[Vývojový plán a harmonogram](vyvojovy_plan.md)** - Fázovaný plán implementace s časovým harmonogramem a milníky
3. **[Technická dokumentace](technicka_dokumentace.md)** - Podrobný popis architektury, workflow, API a technologií
4. **[Instrukce pro vývojáře](instrukce_pro_vyvojare.md)** - Praktické pokyny pro vývojový tým, best practices a implementační detaily

## Přehled řešení

MedDocAI Anonymizer je specializovaný software pro anonymizaci nestrukturované zdravotnické dokumentace v textové podobě. Produkt je navržen jako kritická komponenta v portfoliu AI řešení společnosti STAPRO ve zdravotnictví.

### Klíčové vlastnosti

- Detekce a anonymizace osobních údajů (PII) a chráněných zdravotních informací (PHI)
- Specializované rozpoznávače pro české formáty identifikátorů a zdravotnickou terminologii
- Využití pokročilých NLP modelů (XLM-RoBERTa) pro kontextovou analýzu
- Flexibilní nasazení (Azure Cloud, lokální infrastruktura, on-premise)
- Modulární architektura založená na mikroslužbách
- Plný soulad s GDPR a dalšími regulacemi

### Architektura řešení

Systém je navržen jako modulární, distribuovaný systém založený na mikroslužbách, který zahrnuje následující komponenty:

- API Gateway
- Služba předzpracování
- Služba detekce PII
- Služba anonymizace
- Služba validace
- Dávkový zpracovatel
- Služba konfigurace
- Databáze
- Fronta zpráv

Technologický stack zahrnuje Python, Microsoft Presidio, FastAPI, PostgreSQL, Docker, Kubernetes a další moderní technologie.

## Jak používat tuto dokumentaci

Pro efektivní využití této dokumentace doporučujeme následující postup:

1. Začněte s **Produktovou specifikací** pro pochopení účelu, funkcí a požadavků na produkt
2. Pokračujte **Vývojovým plánem** pro seznámení s harmonogramem a fázemi implementace
3. Prostudujte **Technickou dokumentaci** pro detailní pochopení architektury a technického řešení
4. Nakonec se zaměřte na **Instrukce pro vývojáře** pro praktické pokyny k implementaci

## Další kroky

Po prostudování dokumentace doporučujeme:

1. Zahájit Fázi 0 (Ověření a rozhodnutí o nasazení) dle vývojového plánu
2. Sestavit vývojový tým podle doporučení v sekci "Potřebné zdroje"
3. Nastavit vývojové prostředí podle instrukcí pro vývojáře
4. Zahájit implementaci základních komponent dle harmonogramu

## Kontakt

Pro další informace nebo podporu kontaktujte tým STAPRO AI na adrese ai@stapro.cz nebo prostřednictvím interního Slack kanálu #meddocai-anonymizer.
