from telegram import constants
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from openai import OpenAI
import tiktoken
import logging
from collections import defaultdict

# Settings
TELEGRAM_TOKEN = "*"
OPENROUTER_API_KEY = "*"
MAX_TOKENS = set_max_tokens
BOT_USERNAME = "@botname"

# OpenRouter Client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    default_headers={"HTTP-Referer": "https://site.address"}
)

# Initialising...
encoding = tiktoken.get_encoding("cl100k_base")
user_contexts = defaultdict(list)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Context param
def count_tokens(text):
    return len(encoding.encode(text))

def trim_context(messages):
    total_tokens = sum(count_tokens(msg["content"]) for msg in messages)
    while total_tokens > MAX_TOKENS and len(messages) > 1:
        removed = messages.pop(1)
        total_tokens -= count_tokens(removed["content"])
    return messages

# Command handler
async def start(update, context):
    chat_id = update.effective_chat.id
    user_contexts[chat_id] = [
        {"role": "system", "content": "You are a laconic assistant. Answer briefly."}
    ]
    await update.message.reply_text('Hi! I'm llm model!')

async def clear_history(update, context):
    chat_id = update.effective_chat.id
    user_contexts[chat_id] = [
        {"role": "system", "content": "History cleared. Нou are a short and useful assistant."}
    ]
    await update.message.reply_text("History cleared!")

async def handle_message(update, context):
    # Ignore messages w/o reply (stickers, photo etc.)
    if not update.message.text:
        return
    
    chat_id = update.effective_chat.id
    message = update.message
    
    # Check response conditions:
    should_respond = False
    
    # 1. Personal messages (we always reply)
    if message.chat.type == "private":
        should_respond = True
        user_text = message.text
    
    # 2. Group chats:
    else:
        # Reply to bot message (thread)
        if message.reply_to_message and message.reply_to_message.from_user.username == BOT_USERNAME[1:]:
            should_respond = True
            user_text = message.text
        
        # Direct appeal via @username
        elif BOT_USERNAME.lower() in message.text.lower():
            should_respond = True
            user_text = message.text.replace(BOT_USERNAME, "").strip()
    
    # Leave if you don't need to answer.
    if not should_respond:
        return
    
    # Sending the status "typing..." to the dialog.
    await context.bot.send_chat_action(
        chat_id=chat_id,
        action=constants.ChatAction.TYPING
    )
    
    # Anything + prompt + select a model from the openrouter api
    if not user_contexts[chat_id]:
        user_contexts[chat_id] = [{"role": "system", "content": "You are a useful assistant."}]

    user_contexts[chat_id].append({"role": "user", "content": user_text})
    user_contexts[chat_id] = trim_context(user_contexts[chat_id])

    try:
        response = client.chat.completions.create(
            model="deepseek/deepseek-chat-v3-0324:free",
            messages=user_contexts[chat_id]
        )
        bot_reply = response.choices[0].message.content
        user_contexts[chat_id].append({"role": "assistant", "content": bot_reply})
        
        # Reply to the thread if it is a reply to a bot message
        if message.reply_to_message and message.reply_to_message.from_user.username == BOT_USERNAME[1:]:
            await message.reply_text(bot_reply, reply_to_message_id=message.message_id)
        else:
            await context.bot.send_message(chat_id=chat_id, text=bot_reply)
            
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        await context.bot.send_message(chat_id=chat_id, text="⚠️ An error has occurred. Please try again later.")

# Start this bot
def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("clear", clear_history))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()
    logger.info("The bot has been launched...")

if __name__ == '__main__':
    main()
