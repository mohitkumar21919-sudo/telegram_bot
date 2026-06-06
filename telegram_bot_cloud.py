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

@bot.message_handler(func=lambda m: True)
def handle_any_message(message):
    try:
        # Ignore service messages
        if message.content_type != 'text':
            return
        
        text = message.text.strip()
        if not text:
            return
        
        logger.info(f"Received message: {text}")
        
        # Handle commands - show welcome message
        if text.startswith('/start') or text.startswith('/help'):
            welcome_text = "🎬 Welcome to Movie Bot!\n\nSend a movie name to search:\n• Inception\n• Avatar\n• Iron Man\n• The Dark Knight"
            bot.send_message(message.chat.id, welcome_text)
            return
        
        # Handle search
        query = text.lower()
        results = [m for m in MOVIES if query in m['title'].lower()]
        
        if not results:
            bot.send_message(message.chat.id, f"❌ Not found: {query}\n\nTry: Inception, Avatar, Iron Man, The Dark Knight")
            logger.info(f"No results for: {query}")
            return
        
        logger.info(f"Found {len(results)} results for: {query}")
        for movie in results[:3]:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("📥 Download", callback_data=f"dl_{movie['id']}"))
            markup.add(InlineKeyboardButton("🎬 Stream", callback_data=f"st_{movie['id']}"))
            
            bot.send_message(message.chat.id, f"🎬 *{movie['title']}* ({movie['year']})", reply_markup=markup, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in handle_any_message: {e}")
        try:
            bot.send_message(message.chat.id, f"❌ Error occurred: {str(e)}")
        except:
            pass

@bot.callback_query_handler(func=lambda c: True)
def handle_button(call):
    try:
        bot.answer_callback_query(call.id, show_alert=False)
        
        if not call.data or '_' not in call.data:
            bot.send_message(call.message.chat.id, "❌ Invalid button action")
            return
        
        parts = call.data.split('_', 1)
        if len(parts) < 2:
            bot.send_message(call.message.chat.id, "❌ Invalid action format")
            return
        
        action, movie_id = parts[0], parts[1]
        
        if action not in ['dl', 'st']:
            bot.send_message(call.message.chat.id, "❌ Unknown action")
            return
        
        movie = next((m for m in MOVIES if m['id'] == movie_id), None)
        
        if not movie:
            bot.send_message(call.message.chat.id, f"❌ Movie '{movie_id}' not found in database")
            return
        
        if action == 'dl':
            text = f"*Download {movie['title']}*\n\n[🔍 Search](https://www.google.com/search?q={urllib.parse.quote(movie['title'])})\n[🎬 HDHub4u](https://hdhub4u.xyz)"
        else:
            text = f"*Stream {movie['title']}*\n\n[🎬 HDHub4u](https://hdhub4u.xyz)\n[🔗 Mirror](https://hdhub4u.site)"
        
        bot.send_message(call.message.chat.id, text, parse_mode='Markdown')
        logger.info(f"Button clicked: {action} - {movie_id}")
    except Exception as e:
        logger.error(f"Error in handle_button: {e}")
        try:
            bot.send_message(call.message.chat.id, f"❌ Error: {str(e)}")
        except:
            pass

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
