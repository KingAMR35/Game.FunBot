import telebot
import time
from random import choice
import os
from dotenv import load_dotenv
from api_service import FusionBrainAPI
from telebot import types
from bs4 import BeautifulSoup as b
import random
import requests


load_dotenv()
bot = telebot.TeleBot(os.getenv('TOKEN'))

bot.set_my_commands(
    commands=[
        telebot.types.BotCommand("start", "Запускает бота🚀"),
        telebot.types.BotCommand("restart", "Перезагружает бота🔄"),
        telebot.types.BotCommand("joke", "Расскажет шутку🤭"),
        telebot.types.BotCommand("meme", "Скинет вам мем😄"),
        telebot.types.BotCommand("game", "Мини игра🎮"),
        telebot.types.BotCommand("generate", "Генерирует фото📸"),
        telebot.types.BotCommand("info", "Информация о боте📝"),
    ])

last_used = {}
COOLDOWN_SECONDS = 30

image_counter = 0 

URL = 'https://www.anekdot.ru/last/good/'
def parser(url):
    r = requests.get(url)
    soup = b(r.text, 'html.parser')
    anekdots = soup.find_all('div', class_='anekdot')
    return [c.text for c in anekdots]  
list_of_jokes = parser(URL)
random.shuffle(list_of_jokes)


@bot.message_handler(commands=["start"])
def start_bot(message):
    bot.send_message(message.chat.id, f"Привет, {message.chat.first_name}! Я бот для игр, с которым будет всегда весело и хорошо отдохнуть!")
    
    
@bot.message_handler(commands=["restart"])
def restart_bot(message):
    bot.send_message(message.chat.id, "Идёт перезагрузка, ожидайте🔄")
    time.sleep(1)
    bot.send_message(message.chat.id, f"Привет, {message.chat.first_name}! Я бот для игр, с которым будет всегда весело и хорошо отдохнуть!")
    
    
@bot.message_handler(commands=["joke"])
def joke(message):
    list_of_jokes = parser(URL)
    random.shuffle(list_of_jokes)


    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text="Следующий", callback_data="button")
    keyboard.row(button)


    bot.send_message(message.chat.id, list_of_jokes.pop(), reply_markup=keyboard)



@bot.message_handler(commands=['meme'])
def send_mem(message):
    n = random.choice(os.listdir('images'))
    with open('images/' + n, 'rb') as f:  
        bot.send_photo(message.chat.id, f)   


@bot.message_handler(commands=['game'])
def game(message):
    games = ['🎯', '⚽', '🎲', '🎰', '🏀']
    selected_game = choice(games)
    bot.send_message(message.chat.id, f"Ваша игра: {selected_game}")
    bot.send_dice(message.chat.id, selected_game)

@bot.message_handler(commands=["info"])
def info_bot(message):
    keyboard = types.InlineKeyboardMarkup()
    button2 = types.InlineKeyboardButton(text="1.0", callback_data="version_1.0")
    button3 = types.InlineKeyboardButton(text="1.1", callback_data="version_1.1")
    button4 = types.InlineKeyboardButton(text="1.2", callback_data="version_1.2")
    button04 = types.InlineKeyboardButton(text="1.3", callback_data="version_1.3")
    button5 = types.InlineKeyboardButton(text="2.0", callback_data="version_2.0")
    keyboard.row(button2)
    keyboard.row(button3)
    keyboard.row(button4)
    keyboard.row(button04)
    keyboard.row(button5)
    bot.send_message(message.chat.id, "Выберите версию, про которую вы хотите узнать", reply_markup=keyboard)

@bot.message_handler(commands=['generate'])
def handle_message(message):
    global image_counter
    user_id = message.from_user.id
    now = time.time()
    if user_id in last_used and (now - last_used[user_id]) < COOLDOWN_SECONDS:
        bot.reply_to(message, f'Подождите {COOLDOWN_SECONDS} секунд перед повторным использованием команды.')
        return
    last_used[user_id] = now


    bot.send_message(message.chat.id, 'Напиши мне какую-нибудь фразу и я сгенерирую её.')
    bot.register_next_step_handler(message, prompt)
def prompt(message):
    global image_counter
    prompt = message.text
    chat_id = message.chat.id
    bot.send_chat_action(chat_id, 'typing')
    bot.send_message(message.chat.id, "Подождите, идёт отправка фото🔄")
    bot.send_chat_action(chat_id, 'upload_photo')

        

    api = FusionBrainAPI('https://api-key.fusionbrain.ai/', os.getenv('FB_API_KEY'), os.getenv('FB_SECRET_KEY'))
    pipeline_id = api.get_pipeline()
    uuid = api.generate(prompt, pipeline_id)
    files = api.check_generation(uuid)
    
    image_counter += 1
    unique_filename = f"generated_{uuid}.png"
    save_dir = "generated_images/"
    os.makedirs(save_dir, exist_ok=True)
    final_image_path = os.path.join(save_dir, unique_filename)

    api.save_image(files[0], final_image_path)


    with open(final_image_path, 'rb') as file:
        bot.send_photo(chat_id, file)
    bot.delete_message(chat_id, message.message_id + 1)
    bot.delete_message(chat_id, message.message_id - 1)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline_message(call):
    if call.data == 'button':
        list_of_jokes = parser(URL)
        random.shuffle(list_of_jokes)

        old_joke = call.message.text

    # Проверяем, чтобы новый анекдот отличался от старого
        while list_of_jokes[-1] == old_joke:
            random.shuffle(list_of_jokes)

        # Создаем клавиатуру с кнопкой "Следующий"
        keyboard = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text="Следующий", callback_data="button")
        keyboard.row(button)

        # Отправляем следующий анекдот
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=list_of_jokes.pop(), reply_markup=keyboard)
    
    versions = {
        "version_1.0": "Версия 1.0 — Первая публичная версия бота. В ней представлены базовые команды /start и /restart",
        "version_1.1": "Версия 1.1 — Улучшение стабильности исправление многих багов. Улучшение команды /game",
        "version_1.2": "Версия 1.2 — Добавление новых фоток в /meme",
        "version_1.3": "Версия 1.3 — Добавление новой интересной команды /generate, которая основана на искуственном интелекте.",
        "version_2.0": "Версия 2.0 — Глобальное обновление всего бота, а также глобальное улучшение команды /generate, полная переработка команды /joke, используя парсинг из html."
    }

    # Берём описание соответствующей версии
    version_description = versions.get(call.data, "Описание версии не найдено.")

    # Обновляем сообщение с описанием версии
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=version_description)
    
bot.infinity_polling()