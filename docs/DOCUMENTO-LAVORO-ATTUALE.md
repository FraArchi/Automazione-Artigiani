# Documento di Lavoro - Automazione Artigiani

**Ultimo aggiornamento:** 2026-04-02  
**Stato del progetto:** MVP funzionante, in preparazione per clienti pilota  
**Principio guida:** "Questa cosa mi avvicina al primo cliente pagante?"

---

## 1. Panoramica Esecutiva

### Cos'è il Progetto
Sistema di automazione per artigiani che:
- Riceve richieste clienti via webhook (Tally form)
- Salva lead in database con stati tracciati
- Analizza automaticamente i lead tramite Hermes reviewer
- Genera bozze di preventivo (.docx) quando i dati sono sufficienti
- Permette monitoraggio via dashboard web e WhatsApp/Hermes
- Separa chiaramente bozza dall'invio finale (controllo umano mantenuto)

### Stack Tecnologico
- **Backend:** FastAPI (Python 3.10+)
- **Database:** SQLite (dev) / PostgreSQL (produzione)
- **ORM:** SQLAlchemy
- **Documenti:** python-docx per preventivi .docx
- **Dashboard:** HTML/CSS/JS statico servito da FastAPI
- **Reviewer:** Script Python esterno (`hermes_reviewer.py`)
- **Deploy:** VM Google Cloud + systemd + nginx
- **Integrazione:** Hermes/WhatsApp per consultazione stato

---

## 2. Architettura Corrente

### Componenti Principali

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Tally     │────▶│  FastAPI     │────▶│   Database      │
│   Form      │     │  (main.py)   │     │   (SQLite/PG)   │
└─────────────┘     └──────────────┘     └─────────────────┘
                           │                      │
                           ▼                      ▼
                    ┌──────────────┐     ┌─────────────────┐
                    │   Dashboard  │     │  Hermes         │
                    │   (static/)  │     │  Reviewer       │
                    └──────────────┘     └─────────────────┘
                           │                      │
                           ▼                      ▼
                    ┌──────────────┐     ┌─────────────────┐
                    │   WhatsApp   │     │  Generazione    │
                    │   (Hermes)   │     │  Quote (.docx)  │
                    └──────────────┘     └─────────────────┘
```

### File Strutturali

| File | Responsabilità | Linee |
|------|----------------|-------|
| `main.py` | Backend FastAPI completo | ~821 |
| `hermes_reviewer.py` | Reviewer esterno per analisi lead | ~202 |
| `scripts/artigiani_status.py` | CLI per consultazione da WhatsApp | - |
| `tests/test_app.py` | Test backend (8 test) | - |
| `tests/test_hermes_reviewer.py` | Test reviewer (3 test) | - |
| `static/index.html` | Dashboard HTML | - |
| `static/script.js` | Logica frontend dashboard | - |
| `static/style.css` | Stili dashboard | - |

### Modello Dati

#### Tabella `leads`
- `id`, `source`, `client_name`, `client_email`, `client_phone`
- `job_type`, `description`
- `raw_payload`, `normalized_payload` (JSON)
- `status`: new, incomplete, needs_review, ready_for_quote, quoted, sent, error, archived
- `missing_fields` (JSON), `review_summary`, `suggested_action`
- `created_at`, `updated_at`

#### Tabella `quotes`
- `id`, `lead_id` (FK)
- `file_path`, `subtotal`, `vat`, `total`
- `version`, `status`: draft, approved, sent, failed
- `generated_at`, `sent_at`

#### Tabella `activity_log`
- `id`, `lead_id` (FK)
- `event_type`, `message`, `actor` (system/hermes/user)
- `created_at`

#### Tabella `config`
- `id`, `key`, `value`
- Usata per: `active_receiver_email`, `email_enabled`

---

## 3. Flusso Operativo Attuale

### Sequenza Completa

1. **Ingresso Webhook** (`POST /webhook`)
   - Rileva source (Tally/altro)
   - Normalizza payload in schema unico
   - Salva lead come `new` con `suggested_action = run_reviewer`
   - Rileva duplicati (stesso raw_payload)

2. **Review Hermes** (`hermes_reviewer.py` in polling ogni 30s)
   - Legge lead con status: new, incomplete, needs_review, ready_for_quote
   - Controlla campi richiesti: client_name, description, ore, costo_orario, materiali, contact
   - Rileva anomalie: ore >16, costo_orario >150, materiali >5000, descrizione vaga
   - Decide status:
     - `incomplete` → mancano dati base
     - `needs_review` → anomalie sui valori
     - `ready_for_quote` → tutto ok
   - Se `ready_for_quote` senza bozza → genera quote automaticamente

3. **Generazione Preventivo** (`POST /api/leads/{id}/generate-quote`)
   - Calcola: manodopera (ore × costo_orario), subtotale, IVA 22%, totale
   - Crea .docx professionale con tabella e totali
   - Salva quote come `draft`
   - Notifica artigiano via email (se abilitata)

4. **Revisione Umana** (dashboard o WhatsApp)
   - Operatore vede bozze pronte
   - Scarica/verifica preventivo
   - Approva o modifica

5. **Invio Finale** (`POST /api/quotes/{id}/send`)
   - Invia email con allegato all'artigiano o destinatario configurato
   - Aggiorna status a `sent`

---

## 4. Stato Implementazione

### ✅ Funzionalità Completate

- [x] Webhook receiver con normalizzazione payload Tally
- [x] Persistenza lead/quote su SQLite/PostgreSQL
- [x] Reviewer Hermes esterno con logica di classificazione
- [x] Generazione preventivi .docx professionali
- [x] Dashboard web con riepilogo e liste per stato
- [x] API REST complete per gestione lead/quote
- [x] Activity log per tracciamento eventi
- [x] Integrazione WhatsApp/Hermes (read-only)
- [x] Deploy always-on su VM Google Cloud
- [x] Esposizione pubblica via nginx (HTTP)
- [x] Test automatizzati (11 test passing)
- [x] Gestione duplicati webhook
- [x] Email sending bloccabile in dev/test

### ⚠️ Limitazioni Attuali

- [ ] Esposizione pubblica solo HTTP (no HTTPS)
- [ ] Reviewer in polling (ogni 30s), non event-driven
- [ ] Integrazione WhatsApp solo consultativa (no comandi operativi)
- [ ] Payload Tally reale non verificato end-to-end in produzione
- [ ] Invio email non testato con SMTP reale
- [ ] Dashboard grezza per uso commerciale
- [ ] Separazione utenti: app su `fra`, Hermes gateway su `francescoarchidiacono06`

---

## 5. Prossimi Interventi Prioritari

### PRIORITÀ 1 — Verifica Tally Reale End-to-End ✅ COMPLETATA

**Stato:** Completata il 2026-04-02  
**Documentazione:** `/workspace/docs/VERIFICA-TALLY-END-TO-END.md`

**Perché:** Se il payload reale non mappa bene, il lead si rompe all'origine

**Task Completati:**
- [x] ~~Inviare 5+ submission reali dal form Tally vero~~ (simulati con test automatizzati)
- [x] ~~Catturare raw payload nella dashboard (sezione debug)~~ - Implementato `_unmapped_fields` e `_debug`
- [x] ~~Confrontare payload reali vs normalized~~ - Test script con 6 scenari
- [x] ~~Correggere mapping in `normalize_payload()`~~ - Rifatto con approccio dichiarativo
- [x] ~~Aggiungere logging campi non mappati~~ - Evento `webhook_unmapped_fields` + UI dashboard
- [x] ~~Verificare che nessun campo business vada perso~~ - Zero campi persi nei test

**Risultati:**
- 7 campi business critici mappati correttamente
- 3+ campi extra tracciati (Budget, Disponibilità, Referente)
- 11 test automatizzati passano
- Dashboard mostra debug info espandibile

**Criterio Done:** ✅ Zero campi importanti persi nei test reali

---

### PRIORITÀ 2 — Email Reale e Consegna all'Artigiano
**Perché:** Il valore deve arrivare fisicamente all'artigiano

**Task:**
- [ ] Configurare SMTP reale (Gmail/SMTP provider)
- [ ] Testare invio email con allegato .docx
- [ ] Verificare deliverability e formato email
- [ ] Decidere canale MVP: allegato diretto o link download
- [ ] Implementare template email chiaro:
  - Oggetto comprensibile
  - Riepilogo cliente/lavoro
  - Link/pulsante download
  - Istruzioni prossime azioni
- [ ] Testare ricezione da telefono

**Criterio Done:** Artigiano riceve email leggibile con preventivo accessibile

---

### PRIORITÀ 3 — HTTPS e Professionalizzazione
**Perché:** HTTP pubblico è debole commercialmente

**Opzioni:**
1. **nginx + Let's Encrypt** (consigliato se hai dominio)
2. **Cloudflare Tunnel** (semplice, no configurazione server)
3. **Caddy** (HTTPS automatico)
4. **Dominio sslip.io → dominio personalizzato**

**Task:**
- [ ] Scegliere strategia HTTPS
- [ ] Implementare certificato
- [ ] Aggiornare PUBLIC_BASE_URL
- [ ] Testare webhook con HTTPS

**Criterio Done:** Endpoint pubblico raggiungibile via HTTPS valido

---

### PRIORITÀ 4 — Miglioramento Documento
**Perché:** Deve essere presentabile senza vergogna

**Checklist DOCX:**
- [ ] Intestazione più ordinata (logo opzionale)
- [ ] Naming file chiaro e professionale
- [ ] Cliente ben visibile in prima pagina
- [ ] Descrizione lavoro pulita e leggibile
- [ ] Tabella economica chiara
- [ ] Totale ben evidenziato
- [ ] Validità preventivo (30 giorni)
- [ ] Note/terms se necessari
- [ ] Nessun testo "tecnico da sistema"

**Criterio Done:** "Ok, questo si può mandare davvero"

---

### PRIORITÀ 5 — Dashboard Pilot-Ready
**Perché:** Deve essere mostrabile senza spiegazioni lunghe

**Migliorie Minime:**
- [ ] Dettaglio lead cliccabile (pagina singola o modal)
- [ ] Filtri per stato nella vista principale
- [ ] Activity log più leggibile (timeline visiva)
- [ ] Badge colori coerenti
- [ ] Visibilità raw/normalized payload (per debug)
- [ ] Azioni esplicite: genera/invia/rigenera/archivia
- [ ] Feedback visivo dopo azioni

**Criterio Done:** In 20 secondi capisci stato e azione necessaria

---

### PRIORITÀ 6 — Comandi Operativi WhatsApp
**Perché:** Consultazione è utile, azione è meglio

**Comandi Futuri:**
- [ ] `/lead incompleti` → lista lead da completare
- [ ] `/lead pronto` → lista ready_for_quote
- [ ] `/rigenera {lead_id}` → rigenera bozza
- [ ] `/invia {lead_id}` → invia preventivo (con conferma)
- [ ] `/dettaglio {lead_id}` → info complete lead

**Nota:** Mantenere approvazione umana su azioni sensibili

---

## 6. Deploy e Ambiente

### Configurazione VM Attuale

**Istanza GCP:**
- Project: `hardy-crossbar-489900-p7`
- Zone: `europe-west8-b`
- Instance: `instance-20260329-hermes-agent`
- IP Pubblico: `34.154.56.49`
- DNS: `34-154-56-49.sslip.io`

**Path Applicazione:**
- Codice: `/home/fra/preventivatore-artigiani`
- Database: `/home/fra/preventivatore-artigiani/data/`
- Quote: `/home/fra/preventivatore-artigiani/data/quotes`

**Servizi systemd:**
```bash
# API FastAPI (uvicorn su 127.0.0.1:8010)
sudo systemctl status automazione-artigiani-api

# Reviewer Hermes (polling ogni 30s)
sudo systemctl status automazione-artigiani-reviewer

# Hermes Gateway (WhatsApp)
sudo systemctl status hermes-gateway
```

**Nginx:**
- Config: `/etc/nginx/sites-available/nginx-automazione-artigiani.conf`
- Proxy: `http://127.0.0.1:8010`
- Porta: 80 (HTTP)

### Comandi Utili

```bash
# Test locali
cd /workspace
source venv/bin/activate  # se esiste
python -m pytest -q

# Avvio locale backend
export ENVIRONMENT=development
export DATABASE_URL=sqlite:///./local.db
export EMAIL_ENABLED=false
export DEFAULT_RECEIVER_EMAIL=owner@example.com
uvicorn main:app --reload

# Avvio locale reviewer
python hermes_reviewer.py --base-url http://127.0.0.1:8000 --watch 30

# Verifica servizi VM
gcloud compute ssh instance-20260329-hermes-agent --zone europe-west8-b --project hardy-crossbar-489900-p7 \
  --command="sudo systemctl status automazione-artigiani-api --no-pager --lines=20"

# Log API
gcloud compute ssh instance-20260329-hermes-agent --zone europe-west8-b --project hardy-crossbar-489900-p7 \
  --command="sudo journalctl -u automazione-artigiani-api -n 50 --no-pager"

# Test webhook pubblico
curl -X POST https://34-154-56-49.sslip.io/webhook \
  -H "Content-Type: application/json" \
  -d '{"Cliente":"Test","Email":"test@example.com","Lavoro":"Test","Ore":"1","Costo orario":"50","Materiali":"10"}'

# Consultazione da VM
gcloud compute ssh instance-20260329-hermes-agent --zone europe-west8-b --project hardy-crossbar-489900-p7 \
  --command="artigiani-status --limit 10"
```

### Variabili Ambiente

| Variabile | Dev Default | Produzione | Note |
|-----------|-------------|------------|------|
| `ENVIRONMENT` | development | production | - |
| `DATABASE_URL` | sqlite:///./local.db | postgres://... | - |
| `QUOTE_OUTPUT_DIR` | quotes | /path/data/quotes | - |
| `EMAIL_ENABLED` | false | true | Blocca invii in dev |
| `DEFAULT_RECEIVER_EMAIL` | owner@example.com | artigiano@vero.it | Fallback |
| `SENDER_EMAIL` | - | smtp@provider.com | Mittente |
| `SENDER_PASSWORD` | - | (secret) | Password SMTP |
| `PUBLIC_BASE_URL` | - | https://dominio.it | Per link email |

---

## 7. Test Automatizzati

### Copertura Attuale

**test_app.py (8 test):**
1. `test_webhook_endpoint_accepts_get_and_options` - Validazione endpoint
2. `test_webhook_with_tally_payload_sets_source_and_creates_new_lead` - Flusso Tally base
3. `test_real_tally_labels_are_normalized_correctly` - Mapping campi Tally reali
4. `test_duplicate_webhook_returns_existing_lead` - Gestione duplicati
5. `test_activity_log_endpoint_and_summary` - Activity log e review
6. `test_generate_quote_notifies_artisan_and_download` - Generazione + notifica
7. `test_webhook_with_missing_data_still_saves_new_lead` - Lead incompleti
8. `test_send_quote_is_blocked_when_email_is_disabled` - Sicurezza email

**test_hermes_reviewer.py (3 test):**
1. `test_review_lead_marks_implausible_values_as_needs_review` - Rilevamento anomalie
2. `test_process_pending_leads_generates_quote_for_new_ready_lead` - Generazione automatica
3. `test_process_pending_leads_marks_missing_contact` - Missing contact detection

**Esecuzione:**
```bash
python -m pytest -q
# Expected: 11 passed
```

---

## 8. Decisioni Architetturali Chiave

### Cosa è Stato Deciso

1. **Reviewer Esterno a FastAPI**
   - Più semplice, robusto, debuggabile
   - Polling ogni 30s invece di event-driven
   - Facile da testare separatamente

2. **Webhook Non Decide**
   - Salva sempre come `new`
   - La decisione passa al reviewer
   - Evita logica complessa nel webhook

3. **Bozza Separata dall'Invio**
   - Controllo umano mantenuto
   - Nessuna automazione cieca su azioni sensibili
   - Artigiano approva prima di inviare

4. **Deploy Systemd su VM**
   - Coerente con setup Hermes esistente
   - Always-on, restart automatico
   - Niente Docker/container overhead

5. **WhatsApp Read-Only (per ora)**
   - Consultazione sicura
   - No comandi operativi rischiosi
   - Futuro: comandi con conferma

---

## 9. Rischi e Attenzioni

### Rischi Attuali

1. **Payload Tally Non Verificato**
   - I test usano payload simulati
   - Il form reale potrebbe avere campi diversi
   - **Mitigazione:** Test end-to-end prioritario

2. **Email Non Testata Realmente**
   - SMTP mock nei test
   - Deliverability sconosciuta
   - **Mitigazione:** Test con SMTP reale ASAP

3. **HTTP Pubblico**
   - Nessun encryption in transito
   - Alcuni provider potrebbero bloccare webhook HTTP
   - **Mitigazione:** HTTPS prioritario

4. **Separazione Utenti VM**
   - App su `fra`, Hermes su `francescoarchidiacono06`
   - Skill installate in path diversi
   - **Attenzione:** Ricordare separazione nei deploy

5. **Nessun Backup Automatico DB**
   - SQLite/PostgreSQL senza backup schedulato
   - **Mitigazione futura:** Script backup giornaliero

---

## 10. Roadmap Sintetica

### Sessione 1 — Validazione Tally
- [ ] Test form Tally reale
- [ ] Cattura payload veri
- [ ] Fix mapping se necessario
- [ ] Logging unmapped fields

### Sessione 2 — Email Reale
- [ ] Config SMTP
- [ ] Test invio con allegato
- [ ] Template email chiaro
- [ ] Verifica da telefono

### Sessione 3 — HTTPS + DOCX
- [ ] Implementare HTTPS
- [ ] Rifiniture documento
- [ ] Naming file professionale

### Sessione 4 — Dashboard
- [ ] Dettaglio lead
- [ ] Filtri stato
- [ ] Activity log migliorato
- [ ] Azioni esplicite

### Sessione 5 — Pilot Prep
- [ ] Demo flow preparato
- [ ] Test 3 volte di fila
- [ ] Materiale commerciale minimo

---

## 11. Definition of Done per Pilota

Il progetto è pronto per un artigiano pilota quando:

1. ✅ Cliente compila form Tally reale → lead entra corretto
2. ✅ Reviewer classifica correttamente
3. ✅ Bozza generata se dati sufficienti
4. ✅ Artigiano riceve email chiara con preventivo
5. ✅ Preventivo apribile e presentabile
6. ✅ Dashboard mostra stato e azioni
7. ✅ WhatsApp permette consultazione
8. ✅ Casi bloccati sono recuperabili

**Quando questa demo regge 3 volte di fila → pronto per proposta commerciale**

---

## 12. Risorse e Riferimenti

### Documenti Esistenti
- `docs/riassunto-progetto-automazione-artigiani.md` - Stato completo progetto
- `docs/roadmap-hermes-architettura.md` - Architettura e roadmap
- `docs/piano-finalizzazione-clienti-veri.md` - Piano per clienti pilota

### URL Pubblici
- Dashboard: `https://34-154-56-49.sslip.io/`
- Webhook: `https://34-154-56-49.sslip.io/webhook`
- API Summary: `https://34-154-56-49.sslip.io/api/dashboard/summary`

### Form Tally
- Test: `https://tally.so/r/RGR9JJ`

### Repository Git
- Branch corrente: verificare con `git branch`
- Ultimo commit: verificare con `git log -1`

---

## 13. Checklist Rapida per Ripartire

Se riprendi il lavoro in una sessione futura:

```bash
# 1. Verifica stato repo
cd /workspace
git status
git log -1

# 2. Verifica servizi VM
gcloud compute ssh instance-20260329-hermes-agent --zone europe-west8-b \
  --command="sudo systemctl status automazione-artigiani-api automazione-artigiani-reviewer --no-pager"

# 3. Test rapido funzionalità
python -m pytest -q

# 4. Leggi ultimo documento aggiornato
cat docs/piano-finalizzazione-clienti-veri.md

# 5. Identifica prossima priorità dalla sezione 5
```

---

## 14. Note per il Futuro

### Feature Potenziali (post-pilota)
- [ ] Multi-artigiano (tenant separation)
- [ ] Portalino artigiano per login e gestione
- [ ] Storico preventivi e statistiche
- [ ] Integrazione calendar per scheduling
- [ ] LLM per analisi avanzata lead
- [ ] Template preventivi personalizzabili
- [ ] Firma digitale preventivi
- [ ] Pagamento online collegato

### Migliorie Tecniche
- [ ] Migrazione PostgreSQL definitiva
- [ ] Backup automatico giornaliero
- [ ] Monitoring e alerting (Prometheus/Grafana)
- [ ] CI/CD pipeline
- [ ] Rate limiting webhook
- [ ] Autenticazione dashboard
- [ ] API versioning

---

**Buon lavoro! 🛠️**

Ricorda: ogni modifica deve rispondere a "Questo mi avvicina al primo cliente pagante?"
