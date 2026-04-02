# Spec 50 - Pilot readiness

## Obiettivo
Definire il set minimo di condizioni che rende il progetto presentabile e utilizzabile con 1-3 artigiani pilota reali.

## Perché esiste
Senza una definizione esplicita di "pronto per il pilota", si rischia di oscillare tra rifiniture infinite e false partenze.

## Stato attuale rilevante
Il progetto è già oltre la demo fragile:
- webhook, DB, reviewer, bozza DOCX e dashboard esistono
- test automatici esistono
- deploy base esiste

Ma non è ancora automaticamente pilot-ready perché restano da chiudere:
- qualità della validazione Tally reale
- consegna reale all'artigiano
- UX minima del documento e della dashboard
- presentazione professionale minima (es. HTTPS/base URL affidabile)

## Scope
Dentro:
- checklist finale prima del primo pilota
- criteri minimi tecnici e operativi
- decisioni pratiche per presentarsi in modo serio

Fuori:
- piano commerciale completo
- pricing definitivo
- multi-cliente scalabile
- branding avanzato

## Requisiti minimi per dichiarare "pilot-ready"
1. Tally reale verificato
   - almeno 5 submission reali controllate
   - nessun campo business importante perso
2. Reviewer affidabile sul flusso base
   - lead classificati correttamente nei casi comuni
3. Bozza generata davvero
   - il DOCX si apre e si capisce
4. Consegna reale all'artigiano
   - email reale, allegato o link funzionanti
5. Dashboard minima usabile
   - si capisce cosa è successo e cosa fare
6. Ambiente presentabile
   - preferibilmente HTTPS e base URL coerente
7. Errori recuperabili
   - se qualcosa fallisce, lo capisci da log/dashboard

## File coinvolti
Questa spec è trasversale. I riferimenti principali sono:
- `deploy/`
- `README.md`
- `docs/DOCUMENTO-LAVORO-ATTUALE.md`
- `docs/piano-finalizzazione-clienti-veri.md`
- `docs/spec/*.md`

## Checklist finale sintetica
- [ ] CI verde su main
- [ ] Tally reale validato
- [ ] SMTP reale provato
- [ ] delivery all'artigiano verificata da telefono
- [ ] preventivo giudicato mandabile
- [ ] dashboard sufficiente per operare
- [ ] URL pubblico coerente e credibile
- [ ] una demo end-to-end ripetibile documentata

## Criterio di done
Puoi mostrare il flusso a un artigiano reale e dire con onestà:
- “se arriva una richiesta vera, il sistema la prende”
- “la classifica”
- “prepara una bozza”
- “te la consegna”
- “se qualcosa va storto ce ne accorgiamo”

## Rischi
- dichiarare il pilot pronto solo perché il backend funziona in locale
- rimandare sempre il contatto col reale rifugiandosi nel polishing infinito
- concentrarsi sul look prima di aver chiuso il percorso del valore

## Decisioni già prese
- il pilot non richiede perfezione enterprise
- richiede affidabilità sufficiente, chiarezza e recuperabilità degli errori

## Domande aperte
- per il pilot iniziale basta `sslip.io` con HTTPS o serve già un dominio dedicato?
- chi sarà il primo artigiano di prova e qual è il suo caso d'uso più semplice?

## Priorità
Ultima fase di convergenza. Serve a dire “adesso basta planning, si prova davvero”.
