import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import urllib.parse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = '8679423959:AAGYdSA7TbcFUBpRMdYOJR2xOzeX_XLxReg'

MOVIES = [
    {'title': 'Inception', 'year': '2010', 'id': 'tt1375666'},
    {'title': 'Avatar', 'year': '2009', 'id': 'tt0499549'},
    {'title': 'The Dark Knight', 'year': '2008', 'id': 'tt0468569'},
    {'title': 'Interstellar', 'year': '2014', 'id': 'tt0816692'},
    {'title': 'Iron Man', 'year': '2008', 'id': 'tt0371746'},
    {'title': 'Captain America', 'year': '2011', 'id': 'tt0458339'},
    {'title': 'Thor', 'year': '2011', 'id': 'tt0800369'},
    {'title': 'Spider-Man', 'year': '2002', 'id': 'tt0145487'},
    {'title': 'Batman Begins', 'year': '2005', 'id': 'tt0372784'},
    {'title': 'The Matrix', 'year': '1999', 'id': 'tt0133093'},
]

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, parse_mode='Markdown')

@bot.message_handler(commands=['start', 'help'])
def handle_start(message):
    text = "🎬 Welcome to Movie Bot!\n\nSend a movie name to search:\n• Inception\n• Avatar\n• Iron Man\n• The Dark Knight"
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: len(m.text) > 0)
def handle_search(message):
    try:
        query = message.text.lower()
        results = [m for m in MOVIES if query in m['title'].lower()]
        
        if not results:
            bot.send_message(message.chat.id, f"❌ Not found: {query}\n\nTry: Inception, Avatar, Iron Man")
            return
        
        for movie in results[:3]:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("📥 Download", callback_data=f"dl_{movie['id']}"))
            markup.add(InlineKeyboardButton("🎬 Stream", callback_data=f"st_{movie['id']}"))
            
            bot.send_message(message.chat.id, f"*{movie['title']}* ({movie['year']})", reply_markup=markup)
    except Exception as e:
        logger.error(f"Error in handle_search: {e}")
        bot.send_message(message.chat.id, "❌ Error occurred, please try again")

@bot.callback_query_handler(func=lambda c: True)
def handle_button(call):
    try:
        bot.answer_callback_query(call.id)
        
        parts = call.data.split('_')
        if len(parts) != 2:
            bot.send_message(call.message.chat.id, "❌ Invalid action")
            return
        
        action, movie_id = parts
        movie = next((m for m in MOVIES if m['id'] == movie_id), None)
        
        if not movie:
            bot.send_message(call.message.chat.id, "❌ Movie not found")
            return
        
        if action == 'dl':
            text = f"*Download {movie['title']}*\n\n[🔍 Search](https://www.google.com/search?q={urllib.parse.quote(movie['title'])})\n[🎬 HDHub4u](https://hdhub4u.xyz)"
        else:
            text = f"*Stream {movie['title']}*\n\n[🎬 HDHub4u](https://hdhub4u.xyz)\n[🔗 Mirror](https://hdhub4u.site)"
        
        bot.send_message(call.message.chat.id, text)
    except Exception as e:
        logger.error(f"Error in handle_button: {e}")

if __name__ == '__main__':
    print("🚀 Movie Bot Starting with Polling (works on mobile!)...")
    print("🔄 Removing any existing webhooks first...")
    try:
        bot.remove_webhook()
        print("✅ Webhook removed successfully")
    except Exception as e:
        logger.error(f"Webhook removal error: {e}")
    
    try:
        bot.infinity_polling(skip_pending=True)
    except Exception as e:
        logger.error(f"Bot error: {e}")
        bot.infinity_polling(skip_pending=True)
