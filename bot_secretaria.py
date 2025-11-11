from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import datetime
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# --- CONFIGURACIÓN GOOGLE CALENDAR ---
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def obtener_credenciales():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    if not creds:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return creds

# --- CONFIGURACIÓN TELEGRAM ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("No se encontró la variable TELEGRAM_TOKEN. Configúrala en Railway antes de desplegar.")

app = ApplicationBuilder().token(TOKEN).build()

# --- CONEXIÓN A GOOGLE CALENDAR ---
creds = obtener_credenciales()
service = build("calendar", "v3", credentials=creds)

# --- COMANDOS DEL BOT ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "👋 ¡Hola! Soy tu secretaria virtual.\n\n"
        "Puedo ayudarte con:\n"
        "• /saludo - para saludarte\n"
        "• /evento <fecha> <hora> <nombre> - para agendar algo\n"
        "• /agenda - para mostrar tus próximos eventos\n"
    )
    await update.message.reply_text(msg)

async def saludo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.first_name
    await update.message.reply_text(f"¡Hola {user}! Espero que tengas un excelente día ☀️")

async def evento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) < 3:
            await update.message.reply_text("Uso: /evento <YYYY-MM-DD> <HH:MM> <título>")
            return

        fecha = args[0]
        hora = args[1]
        titulo = " ".join(args[2:])

        start_time = datetime.datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")
        end_time = start_time + datetime.timedelta(hours=1)

        event = {
            "summary": titulo,
            "start": {"dateTime": start_time.isoformat(), "timeZone": "America/Bogota"},
            "end": {"dateTime": end_time.isoformat(), "timeZone": "America/Bogota"},
        }

        service.events().insert(calendarId="primary", body=event).execute()
        await update.message.reply_text(f"✅ Evento '{titulo}' agendado para {fecha} a las {hora}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ No se pudo crear el evento: {e}")

async def agenda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        now = datetime.datetime.utcnow().isoformat() + "Z"
        events_result = (
            service.events()
            .list(calendarId="primary", timeMin=now, maxResults=5, singleEvents=True, orderBy="startTime")
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            await update.message.reply_text("📭 No hay eventos próximos.")
            return

        respuesta = "📅 Próximos eventos:\n\n"
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            fecha = start.replace("T", " ").split("+")[0]
            respuesta += f"• {event['summary']} — {fecha}\n"

        await update.message.reply_text(respuesta)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error al obtener la agenda: {e}")

# --- REGISTRO DE COMANDOS ---
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("saludo", saludo))
app.add_handler(CommandHandler("evento", evento))
app.add_handler(CommandHandler("agenda", agenda))

# --- EJECUCIÓN ---
print("🤖 Bot en ejecución con funciones avanzadas...")
app.run_polling()
