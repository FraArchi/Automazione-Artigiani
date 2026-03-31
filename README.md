# Automazione Artigiani

Automazione Artigiani è un progetto per gestire lead di artigiani, farli analizzare da un reviewer Hermes, generare bozze di preventivo e monitorare tutto via API, dashboard e integrazione Hermes/WhatsApp.

## Documento di riferimento

Per il riepilogo completo dello stato del progetto, dell'architettura, del deploy sulla VM e dei prossimi step, leggere prima questo file:

- [docs/riassunto-progetto-automazione-artigiani.md](docs/riassunto-progetto-automazione-artigiani.md)

## Roadmap e architettura

Documento collegato:

- [docs/roadmap-hermes-architettura.md](docs/roadmap-hermes-architettura.md)

## Stato attuale in breve

- backend FastAPI con persistenza lead/quote
- webhook che salva sempre lead come `new`
- reviewer Hermes esterno (`hermes_reviewer.py`) che classifica i lead e genera le bozze
- dashboard/API per consultazione stato
- deploy always-on su VM Google Cloud con systemd
- endpoint pubblico `/webhook` tramite nginx
- integrazione Hermes/WhatsApp tramite comando `artigiani-status`

## File principali

- `main.py`
- `hermes_reviewer.py`
- `scripts/artigiani_status.py`
- `tests/`
- `deploy/`
- `docs/`

## Test

```bash
./venv/bin/python -m pytest -q
```

## Nota pratica

Se devi riprendere il lavoro in una sessione futura, la cosa migliore è partire dal file:

`docs/riassunto-progetto-automazione-artigiani.md`
