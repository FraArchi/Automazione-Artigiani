#!/usr/bin/env python3
"""
Script di test per verificare il mapping dei payload Tally reali.
Simula 5+ submission con strutture diverse basate su payload Tally tipici.
"""

import json
from main import normalize_payload, dumps_json

# Payload Tally reali tipici (basati sulla struttura effettiva di Tally webhook)
TALLY_PAYLOADS = [
    # Test 1: Form base con tutti i campi principali
    {
        "eventId": "evt_123456",
        "eventType": "form.submission",
        "data": {
            "formId": "abc123",
            "responseId": "resp_789",
            "submittedAt": "2026-04-02T10:00:00Z",
            "fields": [
                {"label": "Cliente", "value": "Mario Rossi"},
                {"label": "Email", "value": "mario.rossi@email.com"},
                {"label": "Telefono", "value": "+39 333 1234567"},
                {"label": "Mestiere", "value": "Idraulico"},
                {"label": "Lavoro", "value": "Rifacimento bagno completo"},
                {"label": "Ore", "value": "40"},
                {"label": "Costo orario", "value": "35"},
                {"label": "Prezzo materiali (€)", "value": "1500"},
                {"label": "Note", "value": "Cliente preferisce mattina"},
            ]
        }
    },
    # Test 2: Form con nomi campo alternativi (variazioni Tally)
    {
        "eventId": "evt_123457",
        "eventType": "form.submission",
        "data": {
            "formId": "abc123",
            "responseId": "resp_790",
            "submittedAt": "2026-04-02T11:00:00Z",
            "fields": [
                {"label": "Nome del Cliente", "value": "Giulia Bianchi"},
                {"label": "Telefono/WhatsApp", "value": "+39 347 9876543"},
                {"label": "Mestiere / tipo di attività", "value": "Elettricista"},
                {"label": "Descrizione del lavoro da svolgere", "value": "Impianto elettrico appartamento 80mq"},
                {"label": "Ore di lavoro stimate", "value": "25"},
                {"label": "Costo orario (€)", "value": "40"},
                {"label": "Materiali", "value": "800"},
                {"label": "Materiali necessari", "value": "Cavi, interruttori, placche"},
                {"label": "Urgenza del lavoro", "value": "Media"},
            ]
        }
    },
    # Test 3: Form minimale (solo campi essenziali)
    {
        "eventId": "evt_123458",
        "eventType": "form.submission",
        "data": {
            "formId": "abc123",
            "responseId": "resp_791",
            "submittedAt": "2026-04-02T12:00:00Z",
            "fields": [
                {"label": "Nome", "value": "Luca Verdi"},
                {"label": "email", "value": "luca.verdi@email.com"},
                {"label": "Dettagli", "value": "Riparazione caldaia"},
                {"label": "ore", "value": "3"},
                {"label": "costo_orario", "value": "50"},
                {"label": "materiali", "value": "150"},
            ]
        }
    },
    # Test 4: Form con campi extra non mappati (da tracciare)
    {
        "eventId": "evt_123459",
        "eventType": "form.submission",
        "data": {
            "formId": "abc123",
            "responseId": "resp_792",
            "submittedAt": "2026-04-02T13:00:00Z",
            "fields": [
                {"label": "Cliente", "value": "Anna Neri"},
                {"label": "Email", "value": "anna.neri@email.com"},
                {"label": "Telefono", "value": "+39 320 1112233"},
                {"label": "Indirizzo del Cliente", "value": "Via Roma 10, Milano"},
                {"label": "Mestiere", "value": "Imbianchino"},
                {"label": "Lavoro", "value": "Tinteggiatura 4 stanze"},
                {"label": "Ore", "value": "20"},
                {"label": "Costo orario", "value": "30"},
                {"label": "Prezzo materiali (€)", "value": "400"},
                {"label": "Eventuali note aggiuntive", "value": "Colori già scelti"},
                # Campi extra che potrebbero essere persi
                {"label": "Budget massimo", "value": "2000"},
                {"label": "Disponibilità", "value": "Sabato e domenica"},
                {"label": "Referente", "value": "Marito"},
            ]
        }
    },
    # Test 5: Payload senza data.fields (formato alternativo)
    {
        "source": "tally_direct",
        "Cliente": "Francesco Gialli",
        "Email": "francesco.gialli@email.com",
        "Telefono": "+39 333 4445566",
        "Mestiere": "Falegname",
        "Lavoro": "Armadio su misura",
        "Ore": "15",
        "Costo orario": "45",
        "Materiali": "600",
        "Note": "Legno di quercia",
    },
    # Test 6: Payload con campi vuoti o nulli
    {
        "eventId": "evt_123460",
        "eventType": "form.submission",
        "data": {
            "formId": "abc123",
            "responseId": "resp_793",
            "submittedAt": "2026-04-02T14:00:00Z",
            "fields": [
                {"label": "Cliente", "value": "Elena Blu"},
                {"label": "Email", "value": ""},
                {"label": "Telefono", "value": "+39 350 7778899"},
                {"label": "Mestiere", "value": "Piastrellista"},
                {"label": "Lavoro", "value": ""},
                {"label": "Ore", "value": None},
                {"label": "Costo orario", "value": "35"},
                {"label": "Prezzo materiali (€)", "value": "1000"},
            ]
        }
    },
]

def test_mapping():
    print("=" * 80)
    print("TEST MAPPING PAYLOAD TALLY REALI")
    print("=" * 80)
    
    all_passed = True
    business_critical_fields = ["client_name", "client_email", "client_phone", "description", "ore", "costo_orario", "materiali"]
    
    for i, raw_payload in enumerate(TALLY_PAYLOADS, 1):
        print(f"\n--- TEST {i} ---")
        print(f"Raw payload keys: {list(raw_payload.keys()) if not isinstance(raw_payload.get('data'), dict) else 'data.fields presente'}")
        
        normalized = normalize_payload(raw_payload)
        
        print(f"\nNormalized result:")
        for field in business_critical_fields:
            value = normalized.get(field)
            status = "✅" if value not in (None, "", []) else "⚠️ "
            print(f"  {status} {field}: {repr(value)}")
        
        # Verifica campi business critici
        missing_critical = [f for f in business_critical_fields if normalized.get(f) in (None, "", [])]
        if missing_critical:
            print(f"  ⚠️  Campi business mancanti: {missing_critical}")
        
        # Mostra campi non mappati
        unmapped = normalized.get("_unmapped_fields", {})
        if unmapped:
            print(f"  📋 Campi non mappati ({len(unmapped)}): {list(unmapped.keys())}")
            for key, value in unmapped.items():
                print(f"      - {key}: {repr(value)}")
        else:
            print(f"  ✅ Nessun campo non mappato")
        
        raw_keys = normalized.get("_raw_keys", [])
        print(f"  📊 Totale chiavi raw: {len(raw_keys)}")
        
        # Verifica che nessun campo business sia nei non mappati
        for critical_field in business_critical_fields:
            if critical_field in unmapped:
                print(f"  ❌ ERRORE: Campo business '{critical_field}' trovato nei non mappati!")
                all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ TUTTI I TEST PASSATI: Zero campi business persi")
    else:
        print("❌ ALMENO UN TEST FALLITO: Controllare il mapping")
    print("=" * 80)
    
    return all_passed

if __name__ == "__main__":
    success = test_mapping()
    exit(0 if success else 1)
