# Spec 10 - Validazione reale dei payload Tally

## Obiettivo
Verificare con evidenza reale che il form Tally in uso produca payload mappati correttamente dal backend senza perdere campi business importanti.

## Perché esiste
Il flusso si rompe all'origine se il webhook riceve dati reali diversi da quelli attesi nei test. Anche un solo campo perso silenziosamente riduce il valore del sistema.

## Stato attuale rilevante
Già presenti:
- endpoint `POST /webhook`
- `detect_source()` e `normalize_payload()`
- salvataggio di `raw_payload` e `normalized_payload`
- endpoint interno `GET /api/leads/{id}/mapping-debug`
- log `webhook_unmapped_fields` per campi extra non mappati
- fixture anonimizzato derivato da payload reale in `tests/fixtures/`
- test automatizzati sul mapping

Manca ancora:
- conferma con submission reali del form attuale
- verifica che ciò che arriva in produzione coincida con i casi previsti

## Scope
Dentro:
- invii reali dal form Tally vero
- confronto raw payload vs normalized payload
- verifica campi business minimi
- decisione su come tracciare eventuali campi extra non mappati

Fuori:
- redesign dashboard
- supporto a provider multipli oltre Tally
- telemetria avanzata

## Campi business minimi da non perdere
- nome cliente
- email o telefono del cliente
- descrizione lavoro
- ore stimate
- costo orario
- materiali
- dati artigiano se presenti nel form

## File coinvolti
- `app/services.py`
- `app/routes.py`
- `tests/test_app.py`
- opzionale: nuovo file di test dedicato ai payload reali anonimizzati
- documentazione risultati in `docs/VERIFICA-TALLY-END-TO-END.md`

## Requisiti
1. Eseguire almeno 5 submission reali dal form Tally in uso.
2. Per ogni submission raccogliere:
   - raw payload ricevuto
   - source rilevata
   - normalized payload salvato
   - status iniziale del lead
3. Verificare che nessun campo business importante risulti perso o svuotato per errore di mapping.
4. Se emergono campi extra ricorrenti, decidere esplicitamente se:
   - mapparli
   - ignorarli
   - tracciarli come metadati separati
5. Non mischiare in modo disordinato dato business e metadato tecnico se non strettamente necessario.

## Criterio di done
- esistono esempi reali verificati del payload attuale
- il mapping copre i campi realmente usati dal form
- eventuali campi extra sono una scelta esplicita, non una perdita silenziosa
- la suite test include almeno un caso anonimizzzato derivato da payload reale

## Rischi
- fare affidamento solo su payload simulati
- introdurre debug rumoroso nella UI ufficiale senza bisogno
- mappare campi extra prematuramente senza un caso d'uso

## Decisioni già prese
- il backend deve restare aderente al flusso reale, non a mockup astratti
- il focus è zero perdite sui campi business, non la perfezione tassonomica del payload

## Domande aperte
- conviene salvare anche una struttura separata tipo `mapping_debug`/`unmapped_fields` oppure basta il confronto raw vs normalized durante la fase di validazione?

## Priorità
Alta. È il primo punto di contatto con il dato reale.
