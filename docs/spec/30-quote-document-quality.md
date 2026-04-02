# Spec 30 - Qualità del documento preventivo

## Obiettivo
Portare il DOCX generato da “bozza tecnicamente corretta” a “documento che un artigiano può davvero inoltrare o usare senza imbarazzo”.

## Perché esiste
La qualità percepita del preventivo conta quasi quanto l'automazione. Se il file appare troppo tecnico o grezzo, il valore del sistema cala immediatamente.

## Stato attuale rilevante
Già presenti:
- generazione DOCX via `python-docx`
- struttura base con intestazione, tabella costi e totale
- campi principali già valorizzati dal payload normalizzato

Da migliorare/validare:
- aspetto professionale
- tono del testo
- chiarezza delle sezioni
- usabilità reale del documento

## Scope
Dentro:
- struttura del documento
- contenuti minimi
- tono del testo
- naming file
- checklist di qualità visuale e pratica

Fuori:
- PDF avanzato
- branding complesso multi-cliente
- editor WYSIWYG
- supporto a tutti i mestieri in modo specializzato

## File coinvolti
- `app/services.py` (funzione di creazione del preventivo)
- `tests/test_app.py`
- eventuale cartella futura con template statici, solo se davvero necessaria

## Requisiti
1. Il documento deve mostrare chiaramente:
   - artigiano
   - cliente
   - data
   - oggetto/intervento
   - righe di costo comprensibili
   - subtotale / IVA / totale
2. Il testo deve essere leggibile e non sembrare output interno di un backend.
3. Il nome file deve essere stabile, comprensibile e scaricabile facilmente.
4. Le eventuali note devono apparire utili, non rumorose.
5. Il totale deve essere visivamente evidente.
6. Il documento deve risultare accettabile visto su laptop e aperto da telefono/computer comune.

## Checklist qualitativa
Il documento finale dovrebbe far dire:
- “si capisce subito di cosa si tratta”
- “si vede bene per chi è”
- “si vede quanto costa”
- “non devo ripulirlo prima di mandarlo”

## Criterio di done
- una bozza reale viene aperta e revisionata da te o da un artigiano di prova
- il feedback è: documento mandabile senza doverlo rifare a mano
- non emergono campi confusi, etichette troppo tecniche o impaginazioni imbarazzanti

## Rischi
- investire troppo tempo nel design del documento prima di validare la consegna reale
- complicare troppo il template per casi non ancora necessari
- generare documenti “belli” ma poco chiari nei dati chiave

## Decisioni già prese
- per ora il formato operativo resta DOCX
- la priorità è presentabilità pratica, non perfezione grafica da agenzia

## Domande aperte
- va aggiunta una sezione finale con validità del preventivo / note operative standard?
- conviene inserire recapiti dell'artigiano in modo più esplicito?

## Priorità
Media-alta. Non blocca il motore, ma blocca la credibilità del pilot se trascurata.
