# Spec 40 - Dashboard operativa minima

## Obiettivo
Rendere la dashboard abbastanza chiara da permettere a un operatore di capire in pochi secondi cosa è successo, cosa richiede attenzione e quale azione fare dopo.

## Perché esiste
La dashboard attuale è già utile, ma per il pilot deve diventare più rassicurante e meno dipendente da spiegazioni verbali.

## Stato attuale rilevante
Già presenti:
- homepage dashboard servita da FastAPI
- summary counts
- liste per stato principali
- activity log
- azioni minime su destinatario e invio quote

Manca ancora:
- visibilità più rapida dello stato operativo
- dettaglio lead più chiaro
- ordine delle priorità di lavoro per l'operatore

## Scope
Dentro:
- chiarezza dei blocchi principali
- leggibilità activity log
- migliore supporto alle decisioni operative
- piccoli miglioramenti UI aderenti alla dashboard reale

Fuori:
- rewrite completo della UI
- promozione immediata di `prototypes/stitch/` a UI ufficiale
- component library complessa
- front-end framework nuovo

## Vincoli già decisi
- la UI ufficiale resta `static/`
- `prototypes/stitch/` è solo reference di direzione visiva
- ogni miglioramento deve servire il flusso operativo reale, non un mockup astratto

## File coinvolti
- `static/index.html`
- `static/script.js`
- `static/style.css`
- `app/routes.py`
- eventuali test API se servono nuovi dati

## Requisiti
1. Un operatore deve capire in ~20 secondi:
   - quanti lead nuovi ci sono
   - quali sono incompleti
   - quali richiedono verifica umana
   - quali bozze sono pronte
   - quali preventivi sono già inviati
2. I campi chiave di un lead devono essere immediatamente visibili:
   - cliente
   - fonte
   - descrizione
   - review summary
   - azione consigliata
3. L'activity log deve essere abbastanza leggibile da spiegare gli ultimi eventi senza scavare nel DB.
4. Le azioni disponibili devono essere esplicite e vicine ai casi d'uso reali.
5. Le migliorie UI devono essere incrementali e non rompere il flusso esistente.

## Migliorie candidate
- dettaglio lead cliccabile
- filtro per stato
- ordinamento più utile per priorità
- badge/stati più chiari
- migliore evidenza per `needs_review` e `draft`
- visibilità migliore dei dati minimi di contatto

## Criterio di done
- la dashboard permette di gestire una giornata di lead senza dover aprire codice o DB
- gli stati critici saltano all'occhio
- il flusso non richiede spiegazioni tecniche continue

## Rischi
- usare questa spec per giustificare un redesign estetico troppo precoce
- aggiungere complessità frontend prima di aver chiuso la validazione Tally e la consegna all'artigiano
- rincorrere il mockup stitch invece del prodotto reale

## Decisioni già prese
- niente rewrite completo in questa fase
- miglioramenti piccoli, verificabili, legati a task reali

## Domande aperte
- serve una vista dettaglio lead dedicata già nel pilot, o basta una card espandibile?
- quali azioni operative devono essere disponibili direttamente in dashboard e quali no?

## Priorità
Media. Va fatta dopo i colli di bottiglia del valore reale.
