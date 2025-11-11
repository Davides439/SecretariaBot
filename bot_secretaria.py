from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Soy tu secretaria virtual. ¿En qué puedo ayudarte?")

# Aquí leemos el token guardado en Railway
TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise ValueError("No se encontró la variable TELEGRAM_TOKEN. Configúrala en Railway antes de desplegar.")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

print("Bot en ejecución...")
app.run_polling()
