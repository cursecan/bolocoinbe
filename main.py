from fastapi import FastAPI, Request, HTTPException, status
from firebase_admin import credentials, firestore
from telebot.async_telebot import AsyncTeleBot
from telebot import types
import telebot
import firebase_admin
import os
import json

BOT_TOKEN = os.environ.get('BOT_TOKEN')
FIREBASE_CONF = os.environ.get('FIREBASE_CONF')

app = FastAPI()
bot = AsyncTeleBot(BOT_TOKEN)

cred = credentials.Certificate(json.loads(FIREBASE_CONF))
firebase_admin.initialize_app(cred)
db = firestore.client()


# @app.on_event('startup')
# async def start_webhook():
#     print('Staring up process')
#     await bot.remove_webhook()

#     await bot.set_webhook(url=WEBHOOK_URL)


# @app.on_event('shutdown')
# async def remove_webhook():
#     await bot.remove_webhook()



@app.get('/')
def index():
    return {
        'message': 'Welcome...'
    }


@app.post('/webhook')
async def webhook(request: Request):
    try:
        json_data = await request.json()
        update = types.Update.de_json(json_data)
        await bot.process_new_updates([update])
        return {
            'status': 'Success'
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@bot.message_handler(commands=['start'])
async def welcome(message):
    user_id = str(message.from_user.id)
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    username = message.from_user.username
    language_code = str(message.from_user.language_code)
    is_premium = message.from_user.is_premium
    welcome_message = (
        f'Hi {first_name}!\n\n'
        f'Welcome to Bolocoin!\n\n'
        f'Here you can earn coin by mining them!\n\n'
    )

    try:
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()

        if not user_doc.exists:
            user_data = {
                'userId': user_id,
                'firstName': first_name,
                'lastName': last_name,
                'username': username,
                'languageCode': language_code,
                'isPremium': is_premium,
                'balance': 0.0,
                'mineRate': 0.001,
                'isMining': False,
                'miningStartDate': None
            }
            
            user_ref.set(user_data)

        await bot.reply_to(message, welcome_message)
    except Exception as e:
        error_message = 'Error, please try again!'
        await bot.reply_to(message, error_message)
        print(f'Error {str(e)}')