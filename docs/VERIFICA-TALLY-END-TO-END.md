# Verifica Tally end-to-end

Data aggiornamento: 2026-04-02
Stato: in corso

## Obiettivo
Verificare con payload reali del form Tally che il backend:
- rilevi correttamente la source
- normalizzi i campi business importanti
- non perda dati utili in modo silenzioso
- renda ispezionabili i campi extra non mappati

## Stato onesto attuale
Completato lato codice:
- mapping dichiarativo in `app/services.py`
- test automatizzati con payload Tally anonimizzato derivato da caso reale
- endpoint interno di debug mapping: `GET /api/leads/{id}/mapping-debug`
- activity log dedicato quando vengono rilevati campi non mappati: `webhook_unmapped_fields`

Non ancora completato lato operativo reale:
- raccolta di almeno 5 submission dal form Tally effettivamente in uso
- conferma sul payload di produzione del form corrente

Quindi:
- il tooling per la verifica è pronto
- la verifica finale con dati reali va ancora eseguita

## Strumenti disponibili

### 1. Raw payload salvato nel lead
Ogni lead salva già:
- `raw_payload`
- `normalized_payload`

### 2. Endpoint di debug mapping
Per un lead esistente:

```bash
curl http://127.0.0.1:8010/api/leads/LEAD_ID/mapping-debug
```

Restituisce:
- `raw_payload`
- `extracted_fields`
- `normalized_payload`
- `mapped_labels_by_field`
- `unmapped_fields`
- `missing_critical_fields`

### 3. Activity log
Se il payload contiene campi extra non mappati, viene registrato:
- `event_type = webhook_unmapped_fields`

## Procedura operativa consigliata

### A. Preparazione
1. Avvia dashboard/API locale o ambiente pubblico.
2. Verifica che il form Tally punti all'endpoint corretto.
3. Tieni aperti:
   - dashboard
   - activity log
   - terminale o curl per interrogare le API

### B. Esegui almeno 5 submission reali
Copri almeno questi casi:
1. lead completo standard
2. lead con label Tally alternative
3. lead con qualche campo mancante
4. lead con almeno un campo extra custom
5. lead con note/urgenza/materiali descrittivi

### C. Per ogni submission verifica
1. il lead è stato creato?
2. `source` è corretta?
3. `normalized_payload` contiene i campi business previsti?
4. `unmapped_fields` contiene solo campi extra attesi?
5. `missing_critical_fields` è coerente con ciò che manca davvero?

## Comandi utili

Lista lead:
```bash
curl http://127.0.0.1:8010/api/leads
```

Debug mapping di un lead:
```bash
curl http://127.0.0.1:8010/api/leads/LEAD_ID/mapping-debug
```

Activity log recente:
```bash
curl 'http://127.0.0.1:8010/api/activity-log?limit=20'
```

## Criterio di done reale
La verifica può dirsi completata quando:
- esistono almeno 5 submission reali del form attuale
- nessun campo business importante viene perso
- gli eventuali campi extra sono visibili e comprensibili
- almeno un caso reale anonimizzato è coperto nei test
- eventuali label nuove vengono mappate o scartate esplicitamente

## Nota importante
Lo stato di questa verifica non va dichiarato “completato” solo perché i test passano. La parte decisiva è il confronto con il payload reale del form in uso.
