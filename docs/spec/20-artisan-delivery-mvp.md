# Spec 20 - Consegna MVP all'artigiano

## Obiettivo
Chiudere il primo flusso che porta valore reale all'artigiano: quando una bozza è pronta, l'artigiano deve riceverla e capire subito cosa fare.

## Perché esiste
Oggi il sistema sa già creare la bozza, ma il progetto non è davvero pilot-ready se l'artigiano non riceve un'esperienza chiara, affidabile e leggibile da telefono.

## Stato attuale rilevante
Già presenti:
- generazione bozza tramite `POST /api/leads/{id}/generate-quote`
- file DOCX salvato su disco
- endpoint download quote
- notifica email supportata a livello codice

Da validare/completare:
- flusso reale di consegna
- contenuto email
- UX del destinatario finale

## Scope
Dentro:
- decisione definitiva canale MVP
- email reale all'artigiano
- allegato vs link download
- testo chiaro e orientato all'azione
- verifica da telefono

Fuori:
- portale clienti completo
- firma elettronica
- approvazioni multilivello
- multi-tenant complesso

## Decisione da fissare in questa spec
Il canale MVP deve essere uno solo e semplice.

Opzioni:
1. Email con allegato DOCX
2. Email con link download
3. Email con entrambi

Raccomandazione iniziale:
- usare entrambi: allegato + link download pubblico controllato
- così l'artigiano ha un fallback immediato

## File coinvolti
- `app/services.py`
- `app/routes.py`
- `hermes_reviewer.py`
- `tests/test_app.py`
- eventuali template testuali in futuro sotto `templates/` se davvero necessari

## Requisiti
1. Quando una bozza viene generata, l'artigiano deve poter ricevere:
   - nome cliente
   - breve riepilogo del lavoro
   - totale bozza
   - istruzione chiara sulla prossima azione
2. L'email deve essere leggibile anche da smartphone.
3. Se esiste allegato, il file deve aprirsi senza problemi.
4. Se esiste link download, il link deve essere corretto e raggiungibile dall'esterno nel contesto pilota.
5. Il testo dell'email non deve sembrare un log tecnico o un output da sistema interno.
6. In caso di fallimento invio, l'evento deve risultare recuperabile e leggibile nell'activity log.

## Criterio di done
- almeno una bozza reale viene consegnata a una casella email reale
- il destinatario riesce ad aprire allegato o link
- il contenuto si capisce subito senza spiegazioni tecniche
- gli errori di invio risultano visibili e diagnosticabili

## Rischi
- concentrarsi su template sofisticati prima di aver validato la consegna vera
- link pubblici non coerenti con HTTPS/base URL
- email formalmente inviata ma inutilizzabile da mobile

## Decisioni già prese
- il controllo umano sull'invio finale va mantenuto
- la priorità è far arrivare il valore, non costruire un portale perfetto

## Domande aperte
- l'email deve arrivare direttamente all'artigiano oppure prima sempre al destinatario attivo interno?
- per il pilota iniziale conviene consegnare solo all'artigiano o anche tenere l'owner in copia?

## Priorità
Altissima. Questa è la prima prova concreta che il sistema produce valore fuori dal server.
