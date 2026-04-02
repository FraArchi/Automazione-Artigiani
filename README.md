# Automazione Artigiani

Automazione Artigiani è un progetto per gestire lead di artigiani, farli analizzare da un reviewer Hermes, generare bozze di preventivo e monitorare tutto via API, dashboard e integrazione Hermes/WhatsApp.

## Documento di Lavoro Principale

Per iniziare a lavorare sul progetto o riprendere dopo una pausa, leggi prima questo file:

- **[docs/DOCUMENTO-LAVORO-ATTUALE.md](docs/DOCUMENTO-LAVORO-ATTUALE.md)** - Panoramica completa, stato attuale, priorità e prossimi interventi

## Altri Documenti di Riferimento

- [docs/riassunto-progetto-automazione-artigiani.md](docs/riassunto-progetto-automazione-artigiani.md) - Storia dettagliata del progetto
- [docs/roadmap-hermes-architettura.md](docs/roadmap-hermes-architettura.md) - Architettura e roadmap strategica
- [docs/piano-finalizzazione-clienti-veri.md](docs/piano-finalizzazione-clienti-veri.md) - Piano per clienti pilota

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
