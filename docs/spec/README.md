# Spec del progetto

Questa cartella contiene una versione snella delle specifiche operative per portare Automazione Artigiani dall'MVP attuale a un pilot credibile per artigiani veri.

Perché questa struttura esiste:
- evitare dispersione in troppi documenti
- mantenere le priorità allineate al codice reale della repo
- descrivere solo i blocchi che sbloccano valore concreto

Ordine di lettura consigliato:
1. `00-ci-and-quality-gates.md`
2. `10-tally-real-validation.md`
3. `20-artisan-delivery-mvp.md`
4. `30-quote-document-quality.md`
5. `40-operator-dashboard-minimum.md`
6. `50-pilot-readiness.md`

Relazione con gli altri documenti:
- `docs/DOCUMENTO-LAVORO-ATTUALE.md` = stato complessivo del progetto
- `docs/riassunto-progetto-automazione-artigiani.md` = contesto storico/architetturale
- `docs/piano-finalizzazione-clienti-veri.md` = obiettivo business e priorità
- `docs/ui-direction.md` = decisione su stitch/prototipi UI

Principi guida di queste spec:
- ogni spec deve avvicinare al primo cliente pagante
- no over-engineering da team enterprise
- priorità al flusso reale: lead -> review -> bozza -> consegna -> invio
- criterio di done sempre verificabile

Stato corrente del progetto alla data di scrittura:
- repo pulita e modulare (`app/`, `main.py` compatibile)
- test automatici verdi
- webhook e reviewer funzionanti
- generazione bozza DOCX funzionante
- dashboard operativa ma ancora essenziale
- consegna reale all'artigiano da validare meglio
