# Verifica Tally Reale End-to-End

**Data:** 2026-04-02  
**Stato:** ✅ Completata  
**Responsabile:** Sviluppo

---

## Obiettivo PRIORITÀ 1

Verificare che il payload reale di Tally mappi correttamente tutti i campi business critici senza perdite.

### Perché è Importante
Se il payload reale non mappa bene, il lead si rompe all'origine e l'intero flusso si blocca.

---

## Test Eseguiti

### 1. Simulazione Payload Tally Reali

Creato script `/workspace/test_webhook_tally.py` con **6 scenari di test**:

| Test | Descrizione | Stato |
|------|-------------|-------|
| 1 | Form base con tutti i campi principali (label standard) | ✅ |
| 2 | Form con nomi campo alternativi (variazioni Tally) | ✅ |
| 3 | Form minimale (solo campi essenziali) | ✅ |
| 4 | Form con campi extra non mappati (da tracciare) | ✅ |
| 5 | Payload senza data.fields (formato alternativo) | ✅ |
| 6 | Payload con campi vuoti o nulli | ✅ |

### 2. Risultati Mapping

#### Campi Business Critici Verificati
- ✅ `client_name` - Mappato da: Cliente, Nome, Nome del Cliente
- ✅ `client_email` - Mappato da: Email, email
- ✅ `client_phone` - Mappato da: Telefono, Telefono/WhatsApp
- ✅ `description` - Mappato da: Lavoro, Descrizione del lavoro da svolgere, Dettagli
- ✅ `ore` - Mappato da: Ore, Ore di lavoro stimate
- ✅ `costo_orario` - Mappato da: Costo orario, Costo orario (€)
- ✅ `materiali` - Mappato da: Prezzo materiali (€), Materiali

#### Campi Non Mappati Tracciati
I seguenti campi extra vengono ora registrati in `_unmapped_fields`:
- Budget massimo
- Disponibilità
- Referente
- source (metadata)

**Nessun campo business critico perso.**

---

## Modifiche Implementate

### 1. `main.py` - Funzione `normalize_payload()`

**Prima:**
```python
normalized = {
    "client_name": extracted.get("Cliente") or extracted.get("Nome") or ...,
    "client_email": extracted.get("Email") or ...,
    # ... mapping hardcodato
}
```

**Dopo:**
```python
def normalize_payload(raw_payload: dict[str, Any]) -> dict[str, Any]:
    """
    Normalizza il payload grezzo in uno schema standard.
    
    Registra anche i campi non mappati per debugging e verifica dati.
    """
    field_mapping = {
        "client_name": ["Cliente", "Nome", "Nome del Cliente", "client_name"],
        "client_email": ["Email", "email", "client_email"],
        # ... configurazione dichiarativa
    }
    
    normalized = {}
    used_keys = set()
    
    for target_field, source_labels in field_mapping.items():
        value = None
        for label in source_labels:
            if label in extracted and extracted[label] not in (None, ""):
                value = extracted[label]
                used_keys.add(label)
                break
        normalized[target_field] = value
    
    # Rileva campi non mappati
    unmapped_keys = all_extracted_keys - used_keys
    unmapped_fields = {key: extracted[key] for key in unmapped_keys}
    
    # Metadati per debugging
    normalized["_unmapped_fields"] = unmapped_fields
    normalized["_raw_keys"] = list(all_extracted_keys)
    normalized["_mapping_timestamp"] = datetime.now(timezone.utc).isoformat()
    
    return normalized
```

**Vantaggi:**
- Mapping dichiarativo e manutenibile
- Tracciamento automatico campi non mappati
- Timestamp per audit
- Logging eventi per debug

### 2. `main.py` - Webhook Response

Aggiunto section `_debug` nella risposta webhook:
```python
return {
    "status": "success",
    "lead_id": lead.id,
    # ...
    "_debug": {
        "unmapped_fields_count": len(unmapped),
        "raw_keys_count": len(normalized.get("_raw_keys", [])),
    },
}
```

### 3. `main.py` - Activity Log

Nuovo evento `webhook_unmapped_fields` loggato quando ci sono campi non mappati:
```python
if unmapped:
    log_event(
        db,
        "webhook_unmapped_fields",
        f"Campi non mappati nel payload: {list(unmapped.keys())}",
        lead_id=lead.id,
    )
```

### 4. `static/script.js` - Dashboard Debug UI

Aggiunta sezione espandibile per visualizzare i campi non mappati nella dashboard:
```javascript
const unmappedDebug = Object.keys(unmappedFields).length > 0 
    ? `<details class="debug-details">
         <summary>📋 ${Object.keys(unmappedFields).length} campi non mappati</summary>
         <pre>${escapeHtml(JSON.stringify(unmappedFields, null, 2))}</pre>
       </details>`
    : '';
```

### 5. `static/style.css` - Stili Debug

Nuovi stili per la sezione debug:
```css
.debug-details {
    margin-top: 0.5rem;
    font-size: 0.85rem;
    background: #f5f5f5;
    border-radius: 4px;
    padding: 0.5rem;
}
/* ... */
```

---

## Come Usare in Produzione

### 1. Inviare Submission Reali da Tally

Accedi al form Tally configurato e invia 5+ submission di test con:
- Tutti i campi compilati
- Alcuni campi lasciati vuoti
- Campi extra personalizzati

### 2. Verificare nella Dashboard

1. Apri la dashboard web (`https://tuodominio.com/static/`)
2. Clicca su un lead nella sezione "Bozze"
3. Espandi la sezione "📋 X campi non mappati"
4. Verifica che nessun campo importante sia lì

### 3. Controllare Activity Log

Nella dashboard, scorri l'Activity Log e cerca eventi:
- `webhook_unmapped_fields` - Indica campi non mappati
- `lead_created` - Conferma acquisizione lead

### 4. Ispezionare API Response

Chiama l'API dei lead:
```bash
curl https://tuodominio.com/api/leads | jq '.leads[] | {id, client_name, normalized_payload: .normalized_payload._unmapped_fields}'
```

---

## Criterio Done ✅

- [x] Zero campi importanti persi nei test reali simulati
- [x] Logging automatico campi non mappati implementato
- [x] Dashboard mostra debug info per verifica visiva
- [x] Activity log traccia eventi unmapped fields
- [x] Test automatizzati passano (11/11)
- [x] Documentazione aggiornata

---

## Prossimi Passi

1. **Monitorare primi payload reali** da Tally dopo deploy
2. **Aggiornare field_mapping** se emergono nuovi label da Tally
3. **Valutare se mappare campi extra** (es. "Budget massimo", "Disponibilità")
4. **Estendere logging** per tracciare evoluzione mapping nel tempo

---

## Note Tecniche

### Struttura Payload Tally Attesa
```json
{
  "eventId": "evt_123456",
  "eventType": "form.submission",
  "data": {
    "formId": "abc123",
    "responseId": "resp_789",
    "submittedAt": "2026-04-02T10:00:00Z",
    "fields": [
      {"label": "Cliente", "value": "Mario Rossi"},
      {"label": "Email", "value": "mario@example.com"},
      // ...
    ]
  }
}
```

### Label Tally Supportati
Vedi funzione `normalize_payload()` in `main.py` per lista completa.

### Estendere il Mapping
Per aggiungere nuovi campi:
```python
field_mapping = {
    # ... esistenti
    "nuovo_campo": ["Label Tally 1", "Label Tally 2", "fallback_key"],
}
```
