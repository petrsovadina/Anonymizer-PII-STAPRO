# Roadmap MedDocAI Anonymizer

Tento dokument nastiňuje plánovaný vývoj projektu MedDocAI Anonymizer.

## Krátkodobé cíle (Q3-Q4 2025)

*   **Optimalizace výkonu:**
    *   Analýza a profilování stávajícího kódu pro identifikaci úzkých míst.
    *   Optimalizace rychlosti zpracování pro velké objemy textu a dávkové operace.
    *   Snížení nároků na paměť.
*   **Vylepšení stávajících rozpoznávačů:**
    *   Zvýšení přesnosti a pokrytí pro `CZECH_BIRTH_NUMBER` (různé formáty, starší RČ).
    *   Rozšíření slovníku pro `CZECH_MEDICAL_FACILITY` o nová a menší zařízení.
    *   Aktualizace `CZECH_DIAGNOSIS_CODE` podle nejnovějších číselníků.
*   **Uživatelské rozhraní (Streamlit):**
    *   Přidání možnosti konfigurace anonymizačních operátorů přímo v UI (např. typ maskování pro konkrétní entitu).
    *   Vylepšení zpětné vazby pro uživatele během zpracování.
*   **Dokumentace:**
    *   Doplnění podrobnějších příkladů použití pro API.
    *   Vytvoření sekce FAQ na základě častých dotazů.

## Střednědobé cíle (2026)

*   **Podpora nových typů dokumentů:**
    *   Rozšíření schopnosti zpracovávat další formáty souborů (např. `.pdf` s extrakcí textu, `.csv`).
*   **Rozšíření o nové rozpoznávače entit (ČR specifické):**
    *   Identifikace čísel bankovních účtů.
    *   Rozpoznávání IČO/DIČ.
    *   Detekce čísel občanských a řidičských průkazů (pokud relevantní pro zdravotnické dokumenty).
*   **Pokročilé funkce anonymizace:**
    *   Možnost pseudonymizace (nahrazení identifikátorů konzistentními, ale fiktivními hodnotami).
    *   Vývoj mechanismu pro zachování referenční integrity mezi anonymizovanými entitami (např. stejné jméno pacienta nahradit stejným pseudonymem napříč dokumenty).
*   **Integrace s externími systémy:**
    *   Zvážení možností napojení na nemocniční informační systémy (NIS) nebo jiné platformy pro sdílení dat (vyžaduje detailní analýzu bezpečnosti a proveditelnosti).
*   **Testování a evaluace:**
    *   Pravidelné vyhodnocování přesnosti a úplnosti rozpoznávačů na nových datech.
    *   Zavedení sady standardizovaných evaluačních datasetů.

## Dlouhodobé cíle (2027+)

*   **Podpora dalších jazyků:**
    *   Analýza a případná implementace podpory pro slovenštinu nebo němčinu (v kontextu příhraniční péče).
*   **Využití pokročilejších NLP modelů:**
    *   Experimenty s transformátorovými modely (např. BERT, RoBERTa) pro zlepšení kontextuálního rozpoznávání entit.
    *   Fine-tuning modelů na specifických datech ze zdravotnictví.
*   **Federované učení:**
    *   Zkoumání možnosti využití federovaného učení pro trénování modelů na datech z více institucí bez nutnosti centralizace citlivých dat.
*   **Certifikace a soulad s normami:**
    *   Snaha o získání relevantních certifikací pro nástroje zpracovávající citlivá data ve zdravotnictví.

## Možná rozšíření (dle priorit a zdrojů)

*   **Interaktivní editor anonymizace:** Nástroj, kde by uživatel mohl revidovat a upravovat výsledky anonymizace před finálním uložením.
*   **Pokročilá analytika nad anonymizovanými daty:** Možnost generovat statistiky nebo přehledy z anonymizovaných dat (např. četnost diagnóz) bez odhalení PII.
*   **Verzování a auditní stopa:** Záznamy o provedených anonymizačních operacích pro účely auditu a sledovatelnosti.

---

Tato roadmapa je živý dokument a může být upravována na základě zpětné vazby, technologického vývoje a priorit projektu.
