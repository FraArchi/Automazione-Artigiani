# Direzione UI del progetto

Data decisione: 2026-04-02

## Decisione

`prototypes/stitch/` NON è la UI ufficiale in produzione.

Per ora viene adottata come:
- esplorazione visuale
- reference di design
- base per futuri refactor incrementali della dashboard

La UI ufficiale resta quella servita da `static/`.

## Perché questa scelta

Il prototipo stitch comunica meglio un look premium/editoriale, ma oggi il progetto è ancora in una fase in cui la priorità principale è:
- rendere affidabile il flusso lead -> review -> bozza -> invio
- ridurre regressioni
- validare il prodotto con clienti reali

Sostituire subito la dashboard attuale con stitch aumenterebbe il rischio di:
- lavorare più sul look che sul flusso operativo
- introdurre regressioni UI/API non ancora coperte da test
- divergere dal modello reale del prodotto, che oggi è più una console operativa che un builder di preventivi manuali

## Uso corretto di stitch da oggi

Usare `prototypes/stitch/` per:
- palette
- tipografia
- direzione estetica
- componenti futuri della dashboard

NON usarlo ancora come:
- sorgente principale della UI pubblica
- sostituto completo di `static/`
- base per feature nuove senza prima adattarle al flusso reale

## Criteri per promuoverlo a direzione ufficiale

Stitch potrà diventare base ufficiale quando saranno vere tutte queste condizioni:

1. flusso operativo stabile nei test
2. dashboard attuale allineata al prodotto reale
3. bisogni dei primi clienti più chiari
4. piano di migrazione incrementale da `static/` a una UI più strutturata
5. nessuna dipendenza da mockup scollegati dai dati reali

## Strategia consigliata

Approccio incrementale:

1. mantenere `static/` come UI ufficiale
2. prendere da stitch solo i pattern visuali migliori
3. applicarli per piccoli passi alla dashboard reale
4. evitare un rewrite completo finché non si chiude la fase di affidabilità MVP
