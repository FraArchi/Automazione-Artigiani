# Spec 00 - CI e quality gates minimi

## Obiettivo
Impedire che la `main` torni a rompersi per dipendenze mancanti, path hardcoded, file locali tracciati o refactor non verificati.

## Perché esiste
Il progetto ha già avuto regressioni reali su:
- `requirements.txt` incompleto
- test dipendenti da path ambiente-specifici
- file locali indesiderati committati (`local.db`, `venv`, `__pycache__`)

Questa spec non serve a fare DevOps elegante: serve a non perdere fiducia nella branch principale.

## Stato attuale rilevante
Già presenti:
- `requirements.txt`
- test in `tests/`
- repo resa più pulita da `.gitignore`
- suite locale passante

Manca ancora:
- esecuzione automatica dei test su GitHub
- gate espliciti prima del merge

## Scope
Dentro:
- GitHub Actions per install e test
- verifica ambiente pulito
- gate minimi di merge
- eventuale check sintattico leggero

Fuori:
- pipeline di deploy
- linting pesante
- release automation
- coverage enforcement avanzato

## File coinvolti
- creare: `.github/workflows/tests.yml`
- leggere/verificare: `requirements.txt`
- leggere/verificare: `tests/test_app.py`
- leggere/verificare: `tests/test_hermes_reviewer.py`
- eventualmente documentare in: `README.md`

## Requisiti
1. A ogni push e PR su `main` deve partire una pipeline.
2. La pipeline deve:
   - fare checkout repo
   - installare Python
   - creare venv o usare install diretta isolata
   - eseguire `pip install -r requirements.txt`
   - eseguire `python -m pytest -q`
3. La pipeline non deve dipendere da file locali non tracciati.
4. La pipeline deve fallire chiaramente se manca una dipendenza o se un test usa path hardcoded non valido.
5. La `main` non va considerata mergeabile se la pipeline è rossa.

## Criterio di done
- esiste workflow GitHub Actions funzionante
- una PR di prova esegue i test automaticamente
- la pipeline passa sul branch corrente
- una rottura intenzionale di test produce fallimento chiaro

## Rischi
- aggiungere controlli troppo ambiziosi e perdere tempo
- introdurre dipendenze di CI non replicate in locale

## Decisioni già prese
- per ora basta `pytest`
- niente linting complesso se non serve a sbloccare il pilot
- il gate principale è: ambiente pulito + test verdi

## Domande aperte
- vogliamo aggiungere anche `python -m py_compile` ai file principali oppure restare solo su pytest?

## Priorità
Alta. Questa è la cintura di sicurezza del progetto.
