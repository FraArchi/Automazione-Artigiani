---
name: automazione-artigiani-chat
description: Consulta da Hermes/WhatsApp lo stato dei lead e del reviewer del progetto Automazione Artigiani sulla VM.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [automazione-artigiani, whatsapp, vm, reviewer, fastapi]
---

# Automazione Artigiani Chat

## Quando usare questa skill
Usa questa skill quando l'utente da WhatsApp chiede:
- quanti lead ci sono
- stato del reviewer
- lead incompleti o pronti per preventivo
- dettaglio di un lead specifico

## Comandi da eseguire
Per il riepilogo generale:

```bash
artigiani-status
```

Per più lead:

```bash
artigiani-status --limit 20
```

Per il dettaglio di un lead:

```bash
artigiani-status --lead-id 12
```

Per output JSON grezzo:

```bash
artigiani-status --json
```

## Come rispondere all'utente
1. Riporta i conteggi principali: new, incomplete, needs_review, ready_for_quote, draft_quotes.
2. Evidenzia i lead bloccati o incompleti.
3. Se c'è un lead pronto con bozza, segnala che è in review_draft.
4. Se l'utente chiede un lead specifico, usa --lead-id e sintetizza review_summary e missing_fields.

## Note
- L'API locale gira su http://127.0.0.1:8010
- Il reviewer systemd gira ogni 30 secondi
- Il comando artigiani-status usa l'API locale e non modifica nulla
