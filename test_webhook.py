import requests
import json

url = "http://127.0.0.1:8000/webhook"

# Esempio di dati che arriverebbero da un form Tally.so o Google Forms
dati_simulati = {
    "Nome": "Mario Rossi",
    "Azienda": "Edilizia Rossi Srl",
    "Tipologia_Richiesta": "Preventivo Ristrutturazione",
    "Dettagli": "Vorrei un preventivo per il rifacimento completo di un bagno di 10mq, includendo impianto idraulico, piastrelle e sanitari."
}

print("Invio richiesta simulata al server webhook locale...")

try:
    response = requests.post(
        url, 
        headers={"Content-Type": "application/json"},
        data=json.dumps(dati_simulati)
    )

    print(f"Status Code: {response.status_code}")
    print(f"Risposta: {response.json()}")
except requests.exceptions.ConnectionError:
    print("❌ Errore di connessione: Il server webhook non è in esecuzione.")
    print("Avvia il server con il comando: uvicorn main:app --reload")
