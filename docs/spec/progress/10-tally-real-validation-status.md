# Spec 10 - Stato implementazione

## Stato attuale
Parzialmente implementata lato codice e strumenti.

## Cosa è stato fatto
- aggiunto endpoint interno `GET /api/leads/{id}/mapping-debug`
- aggiunto log `webhook_unmapped_fields` quando arrivano campi extra non mappati
- introdotto fixture anonimizzato derivato da payload Tally reale in `tests/fixtures/tally_real_payload_anonymized.json`
- aggiunto test automatico sul debug mapping e sui campi non mappati
- riscritta `docs/VERIFICA-TALLY-END-TO-END.md` in forma onesta e operativa

## Cosa manca per chiuderla davvero
- eseguire almeno 5 submission reali dal form Tally attuale
- verificare i payload reali tramite endpoint di debug e activity log
- decidere esplicitamente eventuali nuovi campi da mappare

## Riepilogo operativo rapido
1. invia submission reali dal form Tally
2. recupera il lead creato da `/api/leads`
3. interroga `/api/leads/{id}/mapping-debug`
4. controlla `unmapped_fields` e `missing_critical_fields`
5. controlla activity log per `webhook_unmapped_fields`
6. aggiorna il mapping solo se i campi extra sono davvero utili

## Nota
Questa spec non va marcata come completata finché non si chiude la verifica con payload reali del form effettivamente in uso.
