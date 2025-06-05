
import spacy
try:
    nlp = spacy.load('czech_model')
    doc = nlp('Test českého textu s jménem Pavel Novák.')
    print(f'✅ Český model funguje: {len(doc)} tokenů')
    print(f'   Tokeny: {[token.text for token in doc]}')
except Exception as e:
    print(f'❌ Chyba českého modelu: {e}')
    
try:
    nlp_en = spacy.load('en_core_web_sm')
    doc_en = nlp_en('Test English text with name John Doe.')
    print(f'✅ Anglický model funguje: {len(doc_en)} tokenů')
except Exception as e:
    print(f'❌ Chyba anglického modelu: {e}')
