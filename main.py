import telebot
import time
from random import choice
import random
import os
from dotenv import load_dotenv
from api_service import FusionBrainAPI

load_dotenv()
bot = telebot.TeleBot(os.getenv('TOKEN'))

bot.set_my_commands(
    commands=[
        telebot.types.BotCommand("start", "Запускает бота🚀"),
        telebot.types.BotCommand("restart", "Перезагружает бота🔄"),
        telebot.types.BotCommand("joke", "Расскажет шутку"),
        telebot.types.BotCommand("meme", "Скинет вам мем"),
        telebot.types.BotCommand("game", "Мини игра"),
        telebot.types.BotCommand("quiz", "Викторина"),
        telebot.types.BotCommand("generate", "Генерирует фото"),
    ])

last_used = {}
COOLDOWN_SECONDS = 30


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
    a = ['Я не расист — у меня даже юмор черный.', 'Кто рискует, тому мало кукушки кукуют…',
        "Идет битва за урожай: — Только фермеры отбили урожай у колорадских жуков — прилетели налоговики!..",
        "В Африке, если человек на 80% состоит из воды, то считается, что он из благополучной семьи.",
        "Мама, смотри, негр тает!— Сыночек, не тает, а какает!",
        "Если идешь охотиться на Годзиллу, то шансы 50:50: либо он тебя…, либо ОНА тебя — зависит от пола Годзиллы…",
        "Что такое наивность? — Предположение о том, что русского человека от выпивки остановит отсутствие закуски.",
        "По зоопарку гуляет девочка с мамой.— Мама! Гляди! Программист! (показывая на гориллу)— Почему?"
        "— А он - как папа: глаза красные, лохматый, и на заднице - мозоль!",
        "Идет как-то один путешественик по дороге и видит камень, а на нем написано: --Направо пойдешь негра найдешь, прямо пойдешь,"
        "в передрягу попадешь, налево пойдешь, дом найдешьИ всё же он выбрал дорогу направо...",
        "--Спокойной ночи, малыши-- с детства научили меня тому, что у каждого говорящего в телевизоре в жопе находится рука кукловода.",
        "Одни думают, что Земля круглая. Другие верят, что она плоская. И только в травмопункте знают правду: земля - скользкая.",
        

]
    bot.send_message(message.chat.id, choice(a))
    time.sleep(10)
    bot.delete_message(message.chat.id, message.message_id +1)
    
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


@bot.message_handler(commands=['generate'])
def handle_message(message):
    user_id = message.from_user.id
    now = time.time()
    if user_id in last_used and (now - last_used[user_id]) < COOLDOWN_SECONDS:
        bot.reply_to(message, f'Подождите {COOLDOWN_SECONDS} секунд перед повторным использованием команды.')
        return
    last_used[user_id] = now


    bot.send_message(message.chat.id, 'Напиши мне какую-нибудь фразу и я сгенерирую её.')
    bot.register_next_step_handler(message, prompt)
def prompt(message):  
    prompt = message.text
    chat_id = message.chat.id
    bot.send_chat_action(chat_id, 'typing')
    bot.send_message(message.chat.id, "Подождите, идёт отправка фото🔄")
    bot.send_chat_action(chat_id, 'upload_photo')
    bot.send_chat_action(chat_id, 'upload_photo')
    bot.send_chat_action(chat_id, 'upload_photo')
    bot.send_chat_action(chat_id, 'upload_photo')
        

    api = FusionBrainAPI('https://api-key.fusionbrain.ai/', os.getenv('FB_API_KEY'), os.getenv('FB_SECRET_KEY'))
    pipeline_id = api.get_pipeline()
    uuid = api.generate(prompt, pipeline_id)
    files = api.check_generation(uuid)
        
    api.save_image(files[0], 'result.png')
    with open('result.png', 'rb') as file:
        bot.delete_message(message.chat.id, message.message_id +1)
        bot.delete_message(message.chat.id, message.message_id -1)
        bot.send_photo(message.chat.id, file)
    os.remove('result.png')


   
    
    
bot.infinity_polling()