# Piano di finalizzazione per clienti veri

Ultimo aggiornamento: 2026-04-01

> Obiettivo: trasformare Automazione Artigiani da MVP tecnico promettente a mini-prodotto realmente proponibile a 1-3 artigiani pilota nell'arco più breve possibile.

## 1. Diagnosi onesta dello stato attuale

Sì, sono d'accordo con te: adesso il progetto funziona, ma non è ancora proponibile con tranquillità a clienti veri.

Perché non è ancora proponibile:
- il webhook pubblico esiste, ma il form Tally reale non è ancora verificato end-to-end contro il payload di produzione
- il sistema genera una bozza .docx, ma il valore non arriva ancora davvero all'artigiano in modo chiaro e usabile
- l'invio email non è ancora testato davvero in condizioni reali
- manca un percorso operativo completo e rassicurante: cliente compila -> artigiano riceve -> artigiano apre/legge/scarica -> decide cosa fare
- l'interfaccia admin è già utile, ma ancora grezza per essere mostrata senza spiegazioni

Quindi lo stato corretto da chiamare è:
- non più demo fragile
- non ancora prodotto pilot-ready
- molto vicino a un pilot MVP vero

## 2. Definizione di "pronto per clienti veri"

Il progetto è pronto per essere proposto a un artigiano pilota quando tutte queste condizioni sono vere:

1. Un cliente compila il form reale Tally e il lead entra correttamente senza campi persi.
2. Il reviewer classifica correttamente il lead.
3. Se i dati bastano, la bozza viene generata davvero.
4. L'artigiano riceve una notifica utile e immediata.
5. L'artigiano può aprire o scaricare il preventivo senza passaggi tecnici.
6. Tu puoi monitorare tutto da dashboard e da WhatsApp.
7. I casi bloccati sono leggibili e recuperabili.
8. Il sistema è abbastanza chiaro da poter essere mostrato senza doverlo giustificare troppo.

## 3. Priorità assolute in ordine business

### Priorità 1 — Verifica Tally reale end-to-end
Questa è la prima cosa da chiudere.

Perché è priorità 1:
- se il payload reale Tally non viene mappato bene, il lead si rompe all'origine
- un solo campo perso silenziosamente distrugge fiducia e valore

Obiettivo concreto:
- inviare almeno 5 submission reali dal form vero Tally
- salvare raw payload reali
- confrontare payload reali vs normalize_payload
- correggere il mapping finché tutti i campi business importanti sono robusti

Criterio di done:
- per i casi reali testati, nessun campo importante viene perso
- source corretta
- nessun lead utile finisce monco per errori di mapping

Implementazione richiesta:
- aggiungere visibilità del raw payload nell'admin oppure in una schermata debug limitata
- loggare in modo chiaro i campi non mappati
- opzionalmente salvare una lista `unmapped_fields`

### Priorità 2 — Far arrivare davvero il valore all'artigiano
Questa è la vera seconda barriera.

Problema attuale:
- il preventivo si genera sul server
- viene inviato all'owner
- ma l'artigiano non ha ancora un'esperienza chiara tipo “è pronto, aprilo qui”

Decisione pratica consigliata:
fare prima un flusso semplice e affidabile per l'artigiano, non perfetto ma usabile subito.

Proposta MVP reale:
- quando la bozza è pronta, il sistema notifica l'artigiano via email
- l'email contiene:
  - nome cliente
  - riepilogo breve
  - stato del lead
  - pulsante/link per scaricare il DOCX
  - opzionalmente link alla dashboard o a una pagina singola del lead

Alternativa ancora più semplice:
- inviare email all'artigiano con preventivo allegato direttamente
- in parallelo mantenere la dashboard per revisione interna

Scelta migliore per velocità:
1. prima email reale all'artigiano con allegato o link download
2. poi eventuale portale migliore

Criterio di done:
- l'artigiano riceve davvero un'email
- riesce ad aprire il documento
- capisce che preventivo è, per quale cliente, e cosa deve fare

### Priorità 3 — Test reale dell'invio email
Finché non vedi una mail reale arrivare con allegato o link funzionante, non sei al livello commercialmente presentabile.

Cosa va testato:
- configurazione SMTP reale
- mittente credibile
- deliverability minima
- oggetto chiaro
- testo utile
- allegato .docx corretto o link download corretto

Criterio di done:
- almeno una prova reale completa su una casella normale
- allegato integro / link funzionante
- contenuto leggibile anche da telefono

### Priorità 4 — Rendere il documento effettivamente presentabile
Il DOCX esiste, ma va validato come documento che un artigiano non si vergogna di inoltrare o usare.

Checklist documento:
- intestazione più ordinata
- naming chiaro
- cliente ben visibile
- descrizione lavoro pulita
- righe economiche comprensibili
- totale ben evidenziato
- eventuali note/validità preventivo
- nessun testo troppo “tecnico da sistema”

Criterio di done:
- tu o tuo padre lo vedete e dite: “ok, questo si può mandare davvero”

### Priorità 5 — Pulizia dashboard per uso quotidiano
La dashboard già aiuta, ma per un uso reale serve essere più rassicurante.

Migliorie minime consigliate:
- dettaglio lead cliccabile
- activity log più leggibile
- badge più chiari
- filtro per stato
- visibilità migliore di source, missing fields e review summary
- azioni esplicite: genera / invia / rigenera / segna risolto

Criterio di done:
- in 20 secondi capisci cosa è successo e cosa richiede attenzione

### Priorità 6 — HTTPS vero e immagine più professionale
Il sistema oggi risponde in HTTP pubblico, che tecnicamente basta per alcuni webhook ma commercialmente è debole.

Serve:
- HTTPS vero
- meglio ancora dominio/subdominio pulito
- eventualmente una landing/admin più ordinata

Questo non è il primissimo blocco se Tally accetta HTTP, ma è importante prima di proporlo a terzi.

## 4. Piano operativo a fasi

## Fase A — Validazione tecnica minima per il pilota
Tempo stimato: breve, priorità massima

Obiettivo:
chiudere i due buchi principali: Tally reale + consegna valore all'artigiano.

Task:
1. Testare il form Tally reale con invii veri
2. Catturare e ispezionare payload reali
3. Sistemare `normalize_payload` finché il mapping è robusto
4. Configurare invio email reale
5. Decidere il canale artigiano MVP:
   - allegato diretto
   - oppure link download
6. Far arrivare una bozza vera a una mailbox reale
7. Validare leggibilità del DOCX finale

Output atteso:
- pipeline completa cliente -> bozza -> artigiano funzionante

## Fase B — Rendere l'esperienza pilot-ready
Tempo stimato: breve/medio

Task:
1. Migliorare dashboard lato operatore
2. Aggiungere pagina dettaglio lead
3. Mostrare raw/normalized payload in modo sicuro per debug
4. Migliorare activity log e timeline operativa
5. Rendere chiaro lo stato del preventivo e l'azione successiva
6. Preparare 2-3 template email puliti

Output atteso:
- sistema abbastanza ordinato da essere mostrato a un artigiano vero

## Fase C — Packaging commerciale minimo
Obiettivo:
non solo farlo funzionare, ma farlo sembrare serio abbastanza da proporlo.

Task:
1. HTTPS + dominio o sottodominio
2. Nome chiaro del servizio nella UI
3. testo UI meno tecnico
4. mini demo flow preparato
5. materiale minimo per proporlo a un pilota:
   - cosa fa
   - cosa riceve l'artigiano
   - quanto tempo fa risparmiare

Output atteso:
- mini-prodotto pilotabile

## 5. Ordine immediato consigliato

Se vuoi massimizzare velocità e probabilità di arrivare davvero al primo artigiano, io farei questo ordine preciso:

### Step 1
Test Tally reale end-to-end

### Step 2
Email reale funzionante
- prima a te
- poi a tuo padre / artigiano di prova

### Step 3
Consegna bozza all'artigiano
- allegato o link download

### Step 4
Miglioria minima del DOCX

### Step 5
Pulizia dashboard essenziale

### Step 6
HTTPS + rifinitura esterna

Questo è l'ordine più business-oriented, non il più “elegante tecnicamente”.

## 6. Scelte consigliate per non bloccarsi

Per non impantanarsi, ti consiglio queste scelte pratiche:

### Sul canale di consegna all'artigiano
Non costruire subito un portale complesso.

Versione veloce:
- email con allegato DOCX
oppure
- email con link semplice di download

### Sulla revisione
Non automatizzare l'invio al cliente finale adesso.

Versione giusta oggi:
- Hermes prepara
- artigiano riceve la bozza
- artigiano controlla
- artigiano decide cosa inviare al cliente

### Sulla UX
Non puntare ora a “bello”.
Punta a:
- chiaro
- leggibile
- affidabile
- presentabile

## 7. Rischi reali da evitare adesso

1. Ottimizzare troppo l'interno senza chiudere il flusso esterno
   - se l'artigiano non riceve nulla, il prodotto non esiste davvero

2. Fidarsi del payload simulato
   - Tally reale va testato davvero

3. Pensare che il DOCX tecnico basti
   - deve essere professionalmente accettabile

4. Tenere la dashboard troppo “dev-centric”
   - tu la capisci, il cliente pilota no

5. Aspettare la perfezione
   - serve un pilot MVP serio, non una suite enterprise

## 8. Definition of Done del mini-progetto pilotabile

Io considererei il progetto “subito utilizzabile con clienti veri” quando puoi dimostrare questa scena senza vergogna:

1. un cliente compila il form Tally reale
2. il lead entra correttamente
3. Hermes lo analizza
4. viene generata la bozza
5. l'artigiano riceve una mail chiara
6. apre il documento o il link
7. capisce subito cosa fare
8. tu vedi tutto in dashboard e da WhatsApp

Quando questa demo regge 3 volte di fila, sei già in zona proposta a cliente pilota.

## 9. Piano di esecuzione consigliato per le prossime sessioni

### Sessione 1
Focus: Tally reale + mapping payload

Deliverable:
- test vero
- eventuale fix mapping
- zero campi persi

### Sessione 2
Focus: email reale + consegna bozza all'artigiano

Deliverable:
- invio reale
- allegato o link funzionante
- verifica da telefono

### Sessione 3
Focus: miglioramento DOCX + pulizia dashboard minima

Deliverable:
- preventivo presentabile
- dashboard più leggibile

### Sessione 4
Focus: HTTPS + confezionamento pilot

Deliverable:
- endpoint credibile
- base per proposta commerciale

## 10. Cosa farei io subito dopo questo piano

Se vuoi la strada più veloce verso l'uso reale, il prossimo task concreto da fare è questo:

1. testare il form Tally vero contro il webhook pubblico
2. subito dopo implementare il flusso di consegna all'artigiano

Nota dall'ultimo test reale eseguito: la submit del form Tally ha mostrato la schermata di conferma, ma nei log del backend pubblico non è arrivato alcun POST /webhook. Questo suggerisce che il webhook Tally reale non sia ancora configurato correttamente verso l'endpoint pubblico attuale oppure non sia attivo nelle impostazioni del form.

Perché questi due sono i veri colli di bottiglia che ti impediscono oggi di partire.

---

## Riassunto ultra-breve

Sì, hai ragione: il progetto funziona ma è ancora grezzo per essere proposto.

Le due barriere principali sono:
- payload Tally reale non ancora verificato end-to-end
- il valore non arriva ancora davvero all'artigiano

Quindi l'ordine giusto è:
1. Tally reale
2. email reale
3. consegna bozza all'artigiano
4. documento presentabile
5. dashboard più pulita
6. HTTPS

Questo è il piano più rapido per trasformare il mini-progetto in qualcosa di subito proponibile a clienti veri.
