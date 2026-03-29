import os
import smtplib
import redis
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from openai import OpenAI
from docx import Document
from datetime import datetime, timedelta
from typing import List

app = FastAPI()

# Configurazione Redis
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Montaggio file statici per la Dashboard
app.mount("/static", StaticFiles(directory="static"), name="static")

# ==========================================
# CONFIGURAZIONE
# ==========================================
QWEN_API_KEY = "sk-9d58c013cd1045a69224fd7dc91bf6c0" 
SENDER_EMAIL = "k.fra.archi@gmail.com"
SENDER_PASSWORD = "wcsh jdzd hglt fsoh" 

client = OpenAI(
    api_key=QWEN_API_KEY,
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1" 
)

# ==========================================
# LOGICA EMAIL E RICEVITORI
# ==========================================

def get_receivers() -> List[str]:
    """Recupera la lista dei ricevitori da Redis."""
    receivers = list(r.smembers("receivers"))
    if not receivers:
        # Fallback se il database è vuoto
        return ["francesco.cybersec@gmail.com"]
    return receivers

def send_email_to_all(file_path: str):
    """Invia l'email a tutti i ricevitori salvati."""
    receivers = get_receivers()
    if not receivers:
        print("⚠️ Nessun ricevitore configurato.")
        return

    print(f"Invio email a {len(receivers)} ricevitori: {receivers}")
    
    for receiver in receivers:
        msg = MIMEMultipart()
        msg['Subject'] = f'Nuovo Preventivo: {os.path.basename(file_path)}'
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver

        body = MIMEText("Ciao,\n\nIn allegato trovi il preventivo professionale generato automaticamente.\n\nSaluti,\nSistema Automazione Artigiani")
        msg.attach(body)

        try:
            with open(file_path, "rb") as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(file_path))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                msg.attach(part)
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.send_message(msg)
            print(f"✅ Email inviata con successo a {receiver}")
        except Exception as e:
            print(f"❌ Errore durante l'invio a {receiver}: {e}")

# ==========================================
# LOGICA PREVENTIVI
# ==========================================

def calculate_costs(data: dict):
    try:
        ore = float(str(data.get('Ore', 0)).replace('€', '').strip())
        costo_orario = float(str(data.get('Costo orario', 0)).replace('€', '').strip())
        materiali = float(str(data.get('Materiali', 0)).replace('€', '').strip())
        manodopera = ore * costo_orario
        subtotale = manodopera + materiali
        iva = subtotale * 0.22
        totale = subtotale + iva
        return {
            "manodopera": manodopera, "materiali": materiali,
            "subtotale": subtotale, "iva": iva, "totale": totale,
            "ore": ore, "costo_orario": costo_orario
        }
    except: return None

def create_professional_quote(data: dict, costs: dict):
    filename = f"Preventivo_{data.get('Cliente', 'Cliente')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    doc = Document()
    header = doc.add_paragraph()
    run = header.add_run(f"{data.get('Nome artigiano', 'Artigiano Locale')}\n")
    run.bold = True
    header.add_run(f"{data.get('Mestiere', 'Professionista')}\n")
    header.alignment = 2
    doc.add_heading('PREVENTIVO DI SPESA', 0)
    doc.add_paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y')}\nValidità: 30gg\nLuogo: Grottaminarda (AV)")
    doc.add_heading(f"Spett.le {data.get('Cliente', 'Cliente')}", level=2)
    doc.add_paragraph(f"Oggetto: {data.get('Lavoro', 'Intervento di manutenzione')}")
    
    table = doc.add_table(rows=1, cols=4); table.style = 'Table Grid'
    hdrs = table.rows[0].cells
    hdrs[0].text = 'Descrizione'; hdrs[1].text = 'Quantità'; hdrs[2].text = 'Prezzo Un.'; hdrs[3].text = 'Totale'
    
    r1 = table.add_row().cells
    r1[0].text = 'Manodopera'; r1[1].text = f"{costs['ore']} h"; r1[2].text = f"€{costs['costo_orario']}"; r1[3].text = f"€{costs['manodopera']}"
    r2 = table.add_row().cells
    r2[0].text = 'Materiali'; r2[1].text = '1'; r2[2].text = f"€{costs['materiali']}"; r2[3].text = f"€{costs['materiali']}"
    
    p = doc.add_paragraph(); p.alignment = 2
    p.add_run(f"\nSubtotale: €{costs['subtotale']:.2f}\nIVA 22%: €{costs['iva']:.2f}\n")
    p.add_run(f"TOTALE: €{costs['totale']:.2f}").bold = True
    doc.save(filename)
    return filename

# ==========================================
# ENDPOINT API E WEBHOOK
# ==========================================

@app.get("/")
async def serve_dashboard():
    return FileResponse("static/index.html")

@app.get("/api/receivers")
async def api_get_receivers():
    return {"receivers": get_receivers()}

@app.post("/api/receivers")
async def api_add_receiver(request: Request):
    data = await request.json()
    email = data.get("email")
    if email:
        r.sadd("receivers", email)
        return {"status": "success"}
    raise HTTPException(status_code=400, detail="Email mancante")

@app.delete("/api/receivers/{email}")
async def api_delete_receiver(email: str):
    r.srem("receivers", email)
    return {"status": "success"}

@app.post("/webhook")
async def receive_form(request: Request):
    try: data_raw = await request.json()
    except: data_raw = await request.form()
    
    data = {}
    if 'data' in data_raw and 'fields' in data_raw['data']:
        for field in data_raw['data']['fields']:
            data[field.get('label')] = field.get('value')
    else: data = dict(data_raw)

    costs = calculate_costs(data)
    if not costs: return {"status": "error"}

    file_path = create_professional_quote(data, costs)
    send_email_to_all(file_path)
    return {"status": "success"}
