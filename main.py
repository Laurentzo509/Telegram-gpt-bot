import os
import telebot
import requests
import json
from flask import Flask

# Récupérer les variables d'environnement
TOKEN = os.getenv("TOKEN")  # Token du bot Telegram
API_URL = os.getenv("API_URL")  # URL de l'API
PORT = int(os.getenv("PORT", 10000))  # Port pour Render (par défaut 10000)

# Initialiser le bot Telegram et Flask
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Start Command
@bot.message_handler(commands=["start"])
def start(message):
    text = "👋 Welcome to KAISEN GPT Use the following commands:\n\n"
    text += "🔹 /ask <question> - Get AI-generated response\n"
    text += "🔹 /help - Get support\n"
    text += "🔹 /admin - Contact Admin\n"
    text += "🔹 /live - View live members count"
    bot.send_message(message.chat.id, text)

# Handle all text messages as questions
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    query = message.text.strip()
    if not query:
        bot.send_message(message.chat.id, "❌ Please enter a question")
        return

    try:
        response = requests.get(API_URL + query)
        if response.status_code == 200:
            response_data = json.loads(response.text)
            ai_response = response_data.get("response", "No response found.")
            bot.send_message(message.chat.id, f"🤖 AI Response:\n{ai_response}")
        else:
            bot.send_message(message.chat.id, f"❌ Error: Unable to fetch response. Status code: {response.status_code}")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ An error occurred: {e}")

# Help Command
@bot.message_handler(commands=["help"])
def help_command(message):
    text = "Need help? Click below to DM me 👇"
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton("💬 Contact Developer", url="https://t.me/Kaisensudo"))
    bot.send_message(message.chat.id, text, reply_markup=keyboard)

# Admin Command
@bot.message_handler(commands=["admin"])
def admin(message):
    bot.send_message(message.chat.id, "👤 Admin: @Kaisensudo")

# Live Command (Show Bot Members Count)
@bot.message_handler(commands=["live"])
def live(message):
    bot_info = bot.get_me()
    chat_info = bot.get_chat(bot_info.id)
    bot.send_message(message.chat.id, f"📊 Total Members: {chat_info.members_count}")

# Route pour vérifier que le bot fonctionne
@app.route('/')
def index():
    return "Bot is running!"

# Démarrer le bot et le serveur Flask
if __name__ == "__main__":
    # Démarrer Flask sur le port spécifié
    app.run(host='0.0.0.0', port=PORT)
    # Démarrer le bot Telegram en mode polling
    bot.polling(none_stop=True)  # none_stop=True pour éviter que le bot ne s'arrête en cas d'erreur
