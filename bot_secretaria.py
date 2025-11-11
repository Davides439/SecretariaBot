from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Soy tu secretaria virtual. ¿En qué puedo ayudarte?")

app = ApplicationBuilder().token(os.getenv("8595014644:AAFItOXlXvpjIKcryCxsLzT9rH5HedTZoe0")).build()

app.add_handler(CommandHandler("start", start))

print("Bot en ejecución...")
app.run_polling()

