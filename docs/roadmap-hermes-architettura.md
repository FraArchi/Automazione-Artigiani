# Roadmap veloce + architettura Hermes/FastAPI/DB

## Obiettivo reale
Portare il progetto da "demo tecnica" a "strumento che aiuta un primo artigiano pagante".

## Principio guida
Ogni modifica deve rispondere a una domanda:
"Questa cosa mi avvicina al primo cliente pagante?"

Se no, non entra ora.

---

## Roadmap veloce

### Fase 1 - Rendere l'MVP affidabile
Priorità assoluta.

1. Spostare tutti i segreti in env vars
2. Aggiungere modalità test/dev senza invio email reale
3. Validare bene i dati in ingresso
4. Salvare ogni richiesta nel DB con stato
5. Separare bozza preventivo da invio finale
6. Sistemare la dashboard perché rifletta il flusso reale

Output atteso:
- nessun segreto nel codice
- niente side effect pericolosi nei test
- ogni richiesta è tracciata
- ogni preventivo ha uno stato chiaro

### Fase 2 - Inserire Hermes come coordinatore
Non come "magia AI", ma come supervisore operativo.

1. Hermes legge le richieste nuove
2. Capisce se i dati bastano o mancano pezzi
3. Classifica le richieste
4. Genera un riepilogo utile per te
5. Suggerisce cosa chiedere al cliente
6. Avvia la generazione della bozza solo quando ha senso

Output atteso:
- meno caos
- meno errori
- meno preventivi generati male
- flusso più ordinato

### Fase 3 - Validazione col primo cliente
1. Scegli 1 tipo di artigiano preciso
2. Fagli usare il sistema su richieste vere
3. Misura se risparmia tempo
4. Vendi il risultato, non la tecnologia

Output atteso:
- 1 cliente pilota
- feedback reale
- prime prove di valore

---

## Architettura consigliata

## 1. Ruoli dei componenti

### FastAPI = motore operativo affidabile
Responsabilità:
- ricevere webhook
- validare input
- salvare lead/richieste
- generare preventivi
- inviare email
- servire dashboard/admin
- esporre API interne

FastAPI NON deve decidere in modo intelligente.
Deve eseguire bene.

### Database = memoria di sistema
Responsabilità:
- richieste in arrivo
- stati delle richieste
- destinatario attivo
- storico preventivi
- errori
- log operativi essenziali

Il DB serve a evitare caos, doppioni e perdita di contesto.

### Hermes = orchestratore/supervisore
Responsabilità:
- leggere nuove richieste
- classificare richieste
- trovare dati mancanti
- proporre azioni
- generare riepiloghi
- monitorare anomalie
- coordinare i passaggi del flusso

Hermes NON dovrebbe avere il controllo cieco dell'invio finale all'inizio.
Meglio approvazione umana sulle azioni sensibili.

---

## 2. Modello dati minimo

### Tabella: config
Per impostazioni globali semplici.
Campi minimi:
- id
- key
- value

Esempi:
- active_receiver_email
- email_enabled
- quote_default_validity_days

### Tabella: leads
Ogni richiesta ricevuta.
Campi minimi:
- id
- source
- client_name
- client_email
- client_phone
- job_type
- raw_payload
- normalized_payload
- status
- missing_fields
- created_at
- updated_at

Status possibili:
- new
- incomplete
- ready_for_quote
- quoted
- sent
- error
- archived

### Tabella: quotes
Ogni bozza/preventivo generato.
Campi minimi:
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

Status possibili:
- draft
- approved
- sent
- failed

### Tabella: events o activity_log
Per tracciare cosa succede.
Campi minimi:
- id
- lead_id
- event_type
- message
- actor
- created_at

Actor esempio:
- system
- hermes
- user

---

## 3. Flusso operativo consigliato

### Step A - Ingresso richiesta
Sorgenti possibili:
- Tally
- WhatsApp in futuro
- form manuale

FastAPI riceve il webhook e fa 4 cose:
1. salva raw payload
2. normalizza i campi
3. valida i minimi
4. crea lead con stato iniziale

Regola:
mai perdere una richiesta anche se è incompleta.

### Step B - Normalizzazione
Crei una funzione che converte input diversi in uno schema unico.

Esempio schema logico:
- cliente
- contatto
- tipo_lavoro
- descrizione
- ore
- costo_orario
- materiali
- note

Così Tally oggi e WhatsApp domani entrano nello stesso formato.

### Step C - Controllo Hermes
Hermes legge i lead con stato new.

Per ogni lead decide:
- incomplete: mancano dati chiave
- ready_for_quote: si può preparare bozza
- needs_review: dati strani o contraddittori

Hermes può anche compilare missing_fields, ad esempio:
- metratura mancante
- materiale non specificato
- urgenza non chiara

### Step D - Bozza preventivo
Solo per lead ready_for_quote.

FastAPI genera:
- calcoli
- documento
- record quote nel DB
- stato draft

### Step E - Revisione umana
Tu vedi in dashboard:
- richiesta
- sintesi Hermes
- dati mancanti o criticità
- bozza preventivo

Tu puoi:
- approvare
- correggere
- bloccare

### Step F - Invio
Solo dopo approvazione.

FastAPI invia email e aggiorna:
- quote.status = sent
- lead.status = sent
- log evento

---

## 4. Come entra Hermes concretamente

## Modalità semplice iniziale
Hermes non deve stare dentro FastAPI.
Meglio come supervisore esterno.

Pattern consigliato:
1. FastAPI espone endpoint interni o legge DB
2. Hermes gira periodicamente o su trigger
3. Hermes legge i lead nuovi
4. Hermes scrive classificazione/suggerimenti
5. FastAPI usa quelle informazioni nella dashboard

### Due opzioni pratiche

#### Opzione A - Hermes via cron/polling
Ogni X minuti Hermes:
- legge lead new
- analizza
- aggiorna stato/note

Vantaggi:
- semplice
- robusto
- facile da debuggare

#### Opzione B - Hermes su trigger webhook interno
Quando arriva un lead, FastAPI chiama un task Hermes.

Vantaggi:
- più rapido
Svantaggi:
- più complesso
- più fragile all'inizio

Per ora consiglio A.

---

## 5. API interne utili

### In FastAPI
- POST /webhook
- GET /api/leads
- GET /api/leads/{id}
- PATCH /api/leads/{id}/status
- POST /api/leads/{id}/generate-quote
- POST /api/quotes/{id}/send
- GET /api/dashboard/summary

### Uso da parte di Hermes
Hermes legge:
- lead nuovi
- lead incompleti
- quote draft

Hermes aggiorna:
- stato lead
- missing_fields
- note di revisione
- priorità

---

## 6. Dashboard minima utile
Non un SaaS bello. Una console utile.

Schermate minime:
1. Richieste nuove
2. Richieste incomplete
3. Bozze da approvare
4. Preventivi inviati
5. Errori recenti

Per ogni lead mostra:
- cliente
- tipo lavoro
- data
- stato
- sintesi Hermes
- campi mancanti
- azione successiva

---

## 7. Decisioni che restano umane all'inizio
Meglio non automatizzare subito:
- invio finale al cliente
- modifica importi
- approvazione di richieste ambigue
- scarto lead

Questo protegge da errori stupidi e ti fa imparare.

---

## 8. Sequenza pratica di implementazione

### Step 1
Pulizia sicurezza e affidabilità
- env vars
- no email reali in test
- log decenti

### Step 2
Nuovo schema DB
- leads
- quotes
- activity_log

### Step 3
Webhook robusto
- salva raw payload
- normalizza
- valida
- assegna stato

### Step 4
Dashboard orientata agli stati
- new
- incomplete
- draft
- sent

### Step 5
Hermes coordinatore
- legge lead new
- scrive classificazione
- suggerisce prossima azione

### Step 6
Test con 1 artigiano reale
- feedback su richieste vere
- niente nuove feature prima del feedback

---

## 9. Frase commerciale consigliata
Non vendere:
"software AI per artigiani"

Vendi:
"Ti aiuto a trasformare richieste confuse in bozze di preventivo già pronte, così perdi meno tempo e rispondi prima."

---

## 10. Scelta consigliata adesso
Focus immediato:
- progetto privato
- 1 categoria di artigiani
- 1 operatore
- 1 destinatario attivo
- 1 flusso semplice e controllabile

Non allargare il perimetro prima del primo cliente pagante.
