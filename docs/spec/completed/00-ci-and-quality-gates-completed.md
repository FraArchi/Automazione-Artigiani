# Spec 00 completata - CI e quality gates minimi

## Stato
Completata il 2026-04-02.

## Cosa è stato implementato
- workflow GitHub Actions per push e pull request su `main`
- install delle dipendenze da `requirements.txt` in ambiente pulito
- smoke check sintattico con `python -m py_compile`
- esecuzione automatica della suite `pytest -q`

## File creati/modificati
- `.github/workflows/tests.yml`

## Comportamento operativo
Quando fai:
- push su `main`
- apri o aggiorni una pull request verso `main`

GitHub esegue automaticamente:
1. checkout del repository
2. setup Python 3.11
3. `pip install -r requirements.txt`
4. `python -m py_compile ...` sui file principali
5. `pytest -q`

## Cosa protegge davvero
Questa CI serve soprattutto a evitare regressioni già viste:
- dipendenze dimenticate
- test che funzionano solo sul tuo PC
- errori sintattici introdotti durante refactor
- merge su `main` con suite rotta

## Verifica locale equivalente
Comandi già verificati localmente:

```bash
python -m py_compile \
  main.py \
  hermes_reviewer.py \
  scripts/artigiani_status.py \
  app/models.py \
  app/routes.py \
  app/runtime.py \
  app/services.py \
  app/settings.py \
  app/utils.py \
  tests/test_app.py \
  tests/test_hermes_reviewer.py

pytest -q
```

## Riepilogo operativo
Regola pratica da qui in poi:
- prima fai commit/push
- poi controlla che la GitHub Action sia verde
- solo dopo consideri sicura una PR o un merge

## Prossima spec consigliata
`docs/spec/10-tally-real-validation.md`
