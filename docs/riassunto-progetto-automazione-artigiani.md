# Riassunto progetto: automazione-artigiani

Ultimo aggiornamento: 2026-04-01

Questo documento riassume lo stato del progetto fino ad ora, così da poter riprendere il lavoro in sessioni future senza ricostruire tutto da zero.

## 1. Obiettivo del progetto

Obiettivo pratico:
portare il progetto da demo tecnica a strumento realmente utile per un artigiano, capace di:
- ricevere richieste cliente via webhook/form
- normalizzare i dati in un formato unico
- salvare ogni lead nel database
- far analizzare il lead a un reviewer Hermes
- generare una bozza di preventivo quando i dati sono sufficienti
- separare la bozza dall'invio finale
- permettere il monitoraggio via dashboard e via Hermes/WhatsApp

Principio guida già definito nel progetto:
"Questa cosa mi avvicina al primo cliente pagante?"

## 2. Architettura attuale

### Componenti logici

1. FastAPI
Responsabilità:
- ricevere webhook
- normalizzare i payload
- salvare lead e quote nel DB
- servire dashboard e API
- generare preventivi DOCX
- inviare email solo quando esplicitamente richiesto

2. Database SQLAlchemy
Tabelle principali:
- config
- leads
- quotes
- activity_log

3. Hermes reviewer esterno
Responsabilità:
- leggere i lead
- classificarli
- segnalare dati mancanti o anomalie
- generare la bozza quando il lead è pronto

4. Dashboard/admin
- index statico già servito da FastAPI
- usa le API per mostrare lead, review e conteggi

5. Integrazione Hermes/WhatsApp
- comando read-only locale `artigiani-status`
- skill installata per permettere a Hermes sulla VM di leggere lo stato dei lead da chat

## 3. Flusso operativo attuale

Flusso reale implementato ora:

1. arriva un webhook su `/webhook`
2. FastAPI normalizza il payload
3. il lead viene sempre salvato come `new`
4. nessuna quote viene generata direttamente dal webhook
5. il reviewer Hermes legge periodicamente i lead
6. il reviewer decide:
   - `incomplete` se mancano dati
   - `needs_review` se ci sono anomalie
   - `ready_for_quote` se il lead è valido
7. se il lead è `ready_for_quote` e non esiste ancora una bozza, il reviewer chiama l'API di generazione bozza
8. la bozza viene salvata come quote `draft`
9. l'invio email resta separato e manuale/logico, non automatico

Questo è un passaggio importante: il webhook non decide più, Hermes reviewer sì.

## 4. Modello dati attuale

### Tabella `leads`
Campi rilevanti:
- id
- source
- client_name
- client_email
- client_phone
- job_type
- description
- raw_payload
- normalized_payload
- status
- missing_fields
- review_summary
- suggested_action
- created_at
- updated_at

Status osservati/progettati:
- new
- incomplete
- needs_review
- ready_for_quote
- quoted
- sent
- error
- archived

### Tabella `quotes`
Campi rilevanti:
- id
- lead_id
- file_path
- subtotal
- vat
- total
- version
- status
- generated_at
- sent_at

Status quote:
- draft
- approved
- sent
- failed

### Tabella `activity_log`
Serve a tracciare eventi di sistema, reviewer e utente.

## 5. Stato del backend FastAPI

File principale:
- `main.py`

Funzionalità principali già presenti:
- configurazione tramite env vars
- bootstrap configurazione `config`
- normalizzazione payload webhook
- persistenza lead e quote
- generazione preventivo `.docx`
- invio email con allegato preventivo
- API di consultazione lead/dashboard
- endpoint per aggiornare la review del lead
- endpoint per generare la quote da lead `ready_for_quote`

### Comportamento attuale del webhook
Endpoint:
- `POST /webhook`

Comportamento attuale:
- salva sempre il lead come `new`
- `missing_fields` iniziale vuoto
- `suggested_action = run_reviewer`
- `review_summary = "Lead acquisito. In attesa della revisione Hermes."`
- non genera direttamente alcuna bozza

Questa scelta è intenzionale e allinea il progetto all'architettura desiderata.

## 6. Stato del reviewer Hermes

File:
- `hermes_reviewer.py`

Funzioni principali:
- `review_lead(lead)`
- `process_pending_leads(api_client, ...)`
- `HttpApiClient`
- CLI con `--base-url`, `--limit`, `--watch`

### Logica del reviewer
Controlli attuali:
- campi richiesti mancanti:
  - client_name
  - description
  - ore
  - costo_orario
  - materiali
- mancanza totale di contatto:
  - né email né telefono -> aggiunge `contact`
- anomalie su valori:
  - ore <= 0 o troppo alte (>16)
  - costo orario <= 0 o troppo alto (>150)
  - materiali negativi o molto alti (>5000)
  - descrizione troppo vaga

Output possibili:
- `incomplete`
- `needs_review`
- `ready_for_quote`

Suggested action possibili:
- `request_missing_fields`
- `human_review`
- `generate_quote`
- `review_draft`

### Comportamento importante
Se il reviewer trova un lead `ready_for_quote` senza bozza:
- aggiorna la review
- chiama `POST /api/leads/{id}/generate-quote`
- poi aggiorna il lead in `review_draft`

## 7. Stato del sistema di preventivi

La generazione quote produce file `.docx` professionali con:
- intestazione artigiano
- oggetto intervento
- tabella manodopera/materiali
- subtotale
- IVA 22%
- totale

I file vengono salvati nella cartella configurata da:
- `QUOTE_OUTPUT_DIR`

In locale tipicamente:
- `quotes/`

Sulla VM:
- `/home/fra/preventivatore-artigiani/data/quotes`

## 8. Configurazione ambiente

File di esempio:
- `.env.example`
- `deploy/.env.vm.example`

Variabili importanti:
- `ENVIRONMENT`
- `DATABASE_URL`
- `QUOTE_OUTPUT_DIR`
- `EMAIL_ENABLED`
- `DEFAULT_RECEIVER_EMAIL`
- `SENDER_EMAIL`
- `SENDER_PASSWORD`

Nota:
- email reale è disattivata in test/dev
- invio quote è bloccato se `EMAIL_ENABLED=false`

## 9. Test automatizzati

Test presenti:
- `tests/test_app.py`
- `tests/test_hermes_reviewer.py`

Copertura attuale più importante:

### `tests/test_app.py`
Verifica che:
- un webhook completo crei un lead `new` senza draft immediato
- un webhook incompleto venga comunque salvato come `new`
- l'invio email sia bloccato quando `EMAIL_ENABLED=false`

### `tests/test_hermes_reviewer.py`
Verifica che:
- valori implausibili vengano marcati `needs_review`
- un lead completo `new` venga promosso a `ready_for_quote` e riceva una bozza
- un lead senza contatto venga marcato `incomplete`

Stato test al momento dell'ultimo controllo:
- `10 passed`

## 10. Deploy always-on sulla VM Google Cloud

VM già esistente riutilizzata:
- project: `hardy-crossbar-489900-p7`
- zone: `europe-west8-b`
- instance: `instance-20260329-hermes-agent`

### Path applicazione sulla VM
- `/home/fra/preventivatore-artigiani`

### Servizi systemd configurati
1. `automazione-artigiani-api`
- uvicorn su `127.0.0.1:8010`
- unit file: `deploy/automazione-artigiani-api.service`

2. `automazione-artigiani-reviewer`
- esegue `python hermes_reviewer.py --base-url http://127.0.0.1:8010 --watch 30`
- unit file: `deploy/automazione-artigiani-reviewer.service`

Questi servizi sono abilitati e partono anche al reboot.

## 11. Esposizione pubblica del backend

È stato configurato nginx sulla VM come reverse proxy.

File:
- `deploy/nginx-automazione-artigiani.conf`

Configurazione attuale:
- porta pubblica: `80`
- proxy verso: `127.0.0.1:8010`

Firewall GCP creato:
- `automazione-artigiani-http`

Tag istanza:
- `automazione-artigiani-web`

### URL pubblici attuali
- root/dashboard: `http://34.154.56.49/`
- summary API: `http://34.154.56.49/api/dashboard/summary`
- webhook pubblico: `http://34.154.56.49/webhook`

Verifica già eseguita:
- POST pubblico a `/webhook`: ok
- reviewer ha processato il lead sulla VM: ok

Nota:
- al momento è HTTP, non HTTPS
- Tally accetta HTTP o HTTPS per webhook, quindi il sistema è già usabile
- futuro miglioramento consigliato: HTTPS vero con dominio/tunnel/reverse proxy adeguato

## 12. Integrazione Hermes / WhatsApp

Obiettivo raggiunto:
consentire a Hermes sulla VM di leggere lo stato del progetto da chat WhatsApp.

### Script aggiunto
- `scripts/artigiani_status.py`

### Endpoint utili aggiunti di recente
- `GET /api/activity-log`
- `GET /api/quotes/{quote_id}/download`

### Wrapper installato sulla VM
Comando disponibile:
- `artigiani-status`

Funzioni:
- riepilogo generale lead/reviewer
- dettaglio di un lead specifico
- output JSON

Esempi:
- `artigiani-status`
- `artigiani-status --limit 20`
- `artigiani-status --lead-id 12`
- `artigiani-status --json`

### Skill installata sulla VM per Hermes
Path skill sulla VM (utente Hermes gateway):
- `/home/francescoarchidiacono06/.hermes/skills/local/automazione-artigiani-chat/SKILL.md`

Questa skill insegna a Hermes/WhatsApp come:
- interrogare i lead
- leggere i conteggi dashboard
- mostrare incompleti / ready_for_quote
- mostrare dettaglio di un lead

### Stato gateway WhatsApp
Il servizio `hermes-gateway` è stato riavviato e verificato.
Health bridge osservato:
- `connected`

## 13. File e cartelle rilevanti del progetto

### File principali codice
- `main.py`
- `hermes_reviewer.py`
- `scripts/artigiani_status.py`

### Test
- `tests/test_app.py`
- `tests/test_hermes_reviewer.py`

### Deploy
- `deploy/automazione-artigiani-api.service`
- `deploy/automazione-artigiani-reviewer.service`
- `deploy/nginx-automazione-artigiani.conf`
- `deploy/.env.vm.example`
- `deploy/artigiani-status-wrapper.sh`
- `deploy/automazione-artigiani-chat.SKILL.md`

### Documentazione già presente
- `docs/roadmap-hermes-architettura.md`
- `docs/riassunto-progetto-automazione-artigiani.md` (questo file)

## 14. Comandi utili per sessioni future

### Test locali
```bash
cd /home/fra/Documenti/progetti/automazione-artigiani
source venv/bin/activate
./venv/bin/python -m pytest -q
```

### Avvio locale backend
```bash
cd /home/fra/Documenti/progetti/automazione-artigiani
source venv/bin/activate
export ENVIRONMENT=development
export DATABASE_URL=sqlite:///./local.db
export EMAIL_ENABLED=false
export DEFAULT_RECEIVER_EMAIL=owner@example.com
export QUOTE_OUTPUT_DIR=quotes
uvicorn main:app --reload
```

### Avvio locale reviewer
```bash
python hermes_reviewer.py --base-url http://127.0.0.1:8000 --watch 30
```

### Verifica servizi sulla VM
```bash
gcloud compute ssh instance-20260329-hermes-agent --zone europe-west8-b --project hardy-crossbar-489900-p7 --command="sudo -- systemctl status automazione-artigiani-api --no-pager --lines=20"

gcloud compute ssh instance-20260329-hermes-agent --zone europe-west8-b --project hardy-crossbar-489900-p7 --command="sudo -- systemctl status automazione-artigiani-reviewer --no-pager --lines=20"

gcloud compute ssh instance-20260329-hermes-agent --zone europe-west8-b --project hardy-crossbar-489900-p7 --command="sudo -- systemctl status hermes-gateway --no-pager --lines=20"
```

### Log principali sulla VM
```bash
gcloud compute ssh instance-20260329-hermes-agent --zone europe-west8-b --project hardy-crossbar-489900-p7 --command="sudo -- journalctl -u automazione-artigiani-api -n 50 --no-pager"

gcloud compute ssh instance-20260329-hermes-agent --zone europe-west8-b --project hardy-crossbar-489900-p7 --command="sudo -- journalctl -u automazione-artigiani-reviewer -n 50 --no-pager"
```

### Health e dashboard pubblica
```bash
curl http://34.154.56.49/api/dashboard/summary
curl http://34.154.56.49/
```

### Test webhook pubblico
```bash
curl -X POST http://34.154.56.49/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "Cliente":"Test",
    "Email":"test@example.com",
    "Telefono":"+393331112223",
    "Lavoro":"Test webhook",
    "Ore":"1",
    "Costo orario":"50",
    "Materiali":"10"
  }'
```

### Consultazione lead dalla VM
```bash
gcloud compute ssh instance-20260329-hermes-agent --zone europe-west8-b --project hardy-crossbar-489900-p7 --command="artigiani-status --limit 10"
```

## 15. Decisioni architetturali importanti già prese

1. Il reviewer è esterno a FastAPI
Scelta voluta per semplicità, robustezza e debuggabilità.

2. Il webhook non decide più lo stato finale
Ora salva sempre `new`, e la decisione passa al reviewer.

3. La bozza preventivo è separata dall'invio finale
Scelta utile per mantenere controllo umano.

4. Il deploy always-on usa systemd sulla VM
Scelta coerente con il setup Hermes/WhatsApp già esistente.

5. La consultazione da WhatsApp è read-only
Per ora Hermes legge e sintetizza, ma non esegue ancora azioni operative sensibili.

## 16. Limiti attuali / cose da ricordare

- L'esposizione pubblica è HTTP e non ancora HTTPS.
- Il reviewer gira ogni 30 secondi, non event-driven.
- L'integrazione WhatsApp al momento è di consultazione, non ancora di comando operativo completo.
- Il progetto gira su utente `fra`, mentre Hermes gateway gira come `francescoarchidiacono06`: questa separazione va ricordata quando si installano skill o helper locali.
- Le credenziali email reali non vanno messe nel documento né in memoria persistente.

## 17. Prossimi step consigliati

Ordine consigliato:

1. HTTPS vero per il backend pubblico
Opzioni possibili:
- nginx + certificato
- dominio/subdominio
- cloudflared tunnel
- Caddy

2. Comandi operativi da WhatsApp
Esempi futuri:
- mostra solo lead incompleti
- rigenera bozza lead X
- approva preventivo lead X
- invia preventivo lead X

3. Migliorare la dashboard
- filtri per stato
- vista reviewer più chiara
- storico eventi più leggibile

4. Aumentare l'intelligenza del reviewer
- regole più avanzate
- classificazione per tipo artigiano
- suggerimenti testuali migliori
- eventuale LLM in un secondo momento

5. Primo test reale con artigiano pilota
- raccogliere richieste vere
- misurare tempo risparmiato
- capire quali dati mancano più spesso

## 18. Skill salvate collegate a questo progetto

### Skill generale di deploy always-on
Salvata come:
- `devops/automazione-artigiani-vm-always-on`

Serve per riapplicare il deploy completo su VM con:
- systemd
- reviewer always-on
- esposizione via nginx
- integrazione Hermes/WhatsApp

### Skill lato WhatsApp per consultazione stato
Sulla VM Hermes:
- `automazione-artigiani-chat`

## 19. Riassunto ultra-breve per ripartire in una prossima sessione

Se in una futura sessione serve ripartire velocemente, il contesto minimo è questo:

- progetto: `automazione-artigiani`
- repo locale: `/home/fra/Documenti/progetti/automazione-artigiani`
- VM: `instance-20260329-hermes-agent`
- app deployata su VM in `/home/fra/preventivatore-artigiani`
- API interna su VM: `127.0.0.1:8010`
- reviewer always-on via systemd ogni 30 secondi
- nginx pubblico su `http://34.154.56.49/`
- webhook pubblico su `http://34.154.56.49/webhook`
- il webhook salva lead `new`
- `hermes_reviewer.py` decide lo stato e genera le bozze
- comando utile da VM/Hermes: `artigiani-status`
- test locali: `6 passed`

Se devi continuare il lavoro, leggi prima questo file e poi `docs/roadmap-hermes-architettura.md`.
