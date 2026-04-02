# Automazione Artigiani

Automazione Artigiani è un progetto per gestire lead di artigiani, farli analizzare da un reviewer Hermes, generare bozze di preventivo e monitorare tutto via API, dashboard e integrazione Hermes/WhatsApp.

## Documento di lavoro principale

Per riprendere il progetto dopo una pausa, parti da qui:

- docs/DOCUMENTO-LAVORO-ATTUALE.md

Documenti collegati:
- docs/riassunto-progetto-automazione-artigiani.md
- docs/roadmap-hermes-architettura.md
- docs/piano-finalizzazione-clienti-veri.md
- docs/VERIFICA-TALLY-END-TO-END.md
- docs/ui-direction.md
- docs/spec/README.md

## Stato attuale in breve

- backend FastAPI con persistenza lead/quote
- webhook che salva sempre lead come `new`
- reviewer Hermes esterno (`hermes_reviewer.py`) che classifica i lead e genera le bozze
- dashboard/API per consultazione stato
- deploy always-on su VM Google Cloud con systemd
- endpoint pubblico `/webhook` tramite nginx
- integrazione Hermes/WhatsApp tramite comando `artigiani-status`
- prototipo UI premium conservato come esplorazione in `prototypes/stitch/`

## File principali

- `main.py` — entrypoint compatibile per FastAPI e test
- `app/` — moduli applicativi (runtime, routes, services, models, settings)
- `hermes_reviewer.py`
- `scripts/artigiani_status.py`
- `tests/`
- `deploy/`
- `docs/`
- `prototypes/`

## Avvio rapido dashboard locale

Non serve attivare manualmente la virtualenv.

```bash
make dashboard
```

Oppure:

```bash
./scripts/start_local_dashboard.sh
```

Dashboard locale:

`http://127.0.0.1:8010/`

Per aprire anche il browser:

```bash
make dashboard-open
```

## Reviewer locale

```bash
make reviewer
```

## Test

```bash
./venv/bin/python -m pytest -q
```

In un ambiente pulito installa le dipendenze prima dei test:

```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```
