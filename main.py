import os
import smtplib
import traceback
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from openai import OpenAI
from docx import Document
from datetime import datetime
from typing import List
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- LOGGING INIZIALE ---
print("🚀 Avvio applicazione...")

app = FastAPI()

# --- Configurazione Database PostgreSQL ---
DATABASE_URL = os.environ.get('DATABASE_URL')
print(f"📡 DATABASE_URL trovato: {'Sì' if DATABASE_URL else 'No'}")

# Render a volte fornisce l'URL con "postgres://", ma SQLAlchemy richiede "postgresql://"
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if not DATABASE_URL:
    print("⚠️ DATABASE_URL non configurato. Utilizzo SQLite locale come fallback.")
    DATABASE_URL = "sqlite:///./local.db"

try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()

    class Config(Base):
        __tablename__ = "config"
        id = Column(Integer, primary_key=True, index=True)
        key = Column(String, unique=True, index=True)
        value = Column(String)

    # Crea le tabelle se non esistono
    Base.metadata.create_all(bind=engine)
    print("✅ Database inizializzato correttamente.")
except Exception as e:
    print(f"❌ Errore durante l'inizializzazione del database: {e}")
    traceback.print_exc()

# Montaggio file statici
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
    print("📂 Cartella 'static' montata.")
else:
    print("⚠️ Cartella 'static' non trovata!")

# --- Configurazione API e Email ---
QWEN_API_KEY = os.environ.get("QWEN_API_KEY", "sk-9d58c013cd1045a69224fd7dc91bf6c0") 
SENDER_EMAIL = "k.fra.archi@gmail.com"
SENDER_PASSWORD = "wcsh jdzd hglt fsoh" 

client = OpenAI(
    api_key=QWEN_API_KEY,
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1" 
)

# --- Gestione Destinatario su PostgreSQL ---

def get_active_receiver() -> str:
    db = SessionLocal()
    try:
        config = db.query(Config).filter(Config.key == "active_receiver").first()
        return config.value if config else "francesco.cybersec@gmail.com"
    finally:
        db.close()

def set_active_receiver(email: str):
    db = SessionLocal()
    try:
        config = db.query(Config).filter(Config.key == "active_receiver").first()
        if config:
            config.value = email
        else:
            config = Config(key="active_receiver", value=email)
            db.add(config)
        db.commit()
    finally:
        db.close()

def send_email_to_active(file_path: str):
    receiver = get_active_receiver()
    print(f"📧 Invio email a: {receiver}")
    msg = MIMEMultipart()
    msg['Subject'] = f'Nuovo Preventivo: {os.path.basename(file_path)}'
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver
    msg.attach(MIMEText(f"Ciao,\n\nIn allegato trovi il preventivo professionale generato automaticamente.\n\nSaluti,\nSistema Automazione Artigiani"))

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
        print(f"❌ Errore durante l'invio dell'email: {e}")

# --- Logica Calcolo e Documento ---

def calculate_costs(data: dict):
    try:
        ore = float(str(data.get('Ore', 0)).replace('€', '').strip())
        costo_orario = float(str(data.get('Costo orario', 0)).replace('€', '').strip())
        materiali = float(str(data.get('Materiali', 0)).replace('€', '').strip())
        manodopera = ore * costo_orario
        subtotale = manodopera + materiali
        iva = subtotale * 0.22
        totale = subtotale + iva
        return {"manodopera": manodopera, "materiali": materiali, "subtotale": subtotale, "iva": iva, "totale": totale, "ore": ore, "costo_orario": costo_orario}
    except Exception as e:
        print(f"❌ Errore nei calcoli: {e}")
        return None

def create_professional_quote(data: dict, costs: dict):
    filename = f"Preventivo_{data.get('Cliente', 'Cliente')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    doc = Document()
    header = doc.add_paragraph()
    header.add_run(f"{data.get('Nome artigiano', 'Artigiano Locale')}\n").bold = True
    header.add_run(f"{data.get('Mestiere', 'Professionista')}\n")
    header.alignment = 2
    doc.add_heading('PREVENTIVO DI SPESA', 0)
    doc.add_paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y')}\nValidità: 30gg\nLuogo: Grottaminarda (AV)")
    doc.add_heading(f"Spett.le {data.get('Cliente', 'Cliente')}", level=2)
    doc.add_paragraph(f"Oggetto: {data.get('Lavoro', 'Intervento di manutenzione')}")
    
    table = doc.add_table(rows=1, cols=4); table.style = 'Table Grid'
    hdrs = table.rows[0].cells
    hdrs[0].text = 'Descrizione'; hdrs[1].text = 'Quantità'; hdrs[2].text = 'Prezzo Un.'; hdrs[3].text = 'Totale'
    
    r1 = table.add_row().cells; r1[0].text = 'Manodopera'; r1[1].text = f"{costs['ore']} h"; r1[2].text = f"€{costs['costo_orario']}"; r1[3].text = f"€{costs['manodopera']}"
    r2 = table.add_row().cells; r2[0].text = 'Materiali'; r2[1].text = '1'; r2[2].text = f"€{costs['materiali']}"; r2[3].text = f"€{costs['materiali']}"
    
    p = doc.add_paragraph(); p.alignment = 2
    p.add_run(f"\nSubtotale: €{costs['subtotale']:.2f}\nIVA 22%: €{costs['iva']:.2f}\n")
    p.add_run(f"TOTALE: €{costs['totale']:.2f}").bold = True
    doc.save(filename)
    return filename

# --- API e Webhook ---

@app.get("/")
async def serve_dashboard():
    if not os.path.exists("static/index.html"):
        return {"error": "Dashboard non trovata in static/index.html"}
    return FileResponse("static/index.html")

@app.get("/api/receivers")
async def api_get_receivers():
    return {"receivers": [get_active_receiver()]}

@app.post("/api/receivers")
async def api_add_receiver(request: Request):
    data = await request.json()
    email = data.get("email")
    if email:
        set_active_receiver(email)
        print(f"✅ Destinatario attivo impostato a: {email}")
        return {"status": "success"}
    raise HTTPException(status_code=400, detail="Email mancante")

@app.delete("/api/receivers/{email}")
async def api_delete_receiver(email: str):
    set_active_receiver("francesco.cybersec@gmail.com") # Reset al default
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

    print(f"🚀 Elaborazione preventivo per: {data.get('Cliente')}")
    costs = calculate_costs(data)
    if not costs: return {"status": "error", "message": "Calcoli falliti"}

    file_path = create_professional_quote(data, costs)
    send_email_to_active(file_path)
    return {"status": "success"}

print("🚀 Applicazione pronta e in ascolto.")
