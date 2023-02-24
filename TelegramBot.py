from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from ChatGPT import ChatGPT
from DataBase import DataBase
from lang import *


class TelegramBot:
  # Инициализация бота
  def __init__(self, api_key_tg, api_keys_gpt, database_file,
               name_bot_command):
    self.bot = Bot(token=api_key_tg)
    self.chatgpt = ChatGPT(api_keys_gpt)
    self.database = DataBase(database_file)
    self.dp = Dispatcher(self.bot)
    self.name_bot_command = name_bot_command

    self.dp.message_handler(commands=["start"])(self.process_start_command)
    self.dp.message_handler(commands=["pay"])(self.pay_command_handler)
    self.dp.message_handler(commands=["info"])(self.info_command_handler)
    self.dp.message_handler(commands=["help"])(self.help_command_handler)
    self.dp.message_handler()(self.echo_message)

    # Запуск бота
    executor.start_polling(self.dp)

  def RegisterUser(self,
                    username,
                    userid,
                    firstname,
                    lastname,
                    banned=0,
                    is_spam=1,
                    balance=0,
                    lang='ru',
                    tokens=500,
                    ratings=0):
      try:
          userdata = self.database.query(f"SELECT * FROM users WHERE userid={userid}")
          if len(userdata) <= 0:
              self.database.query(
                  f"INSERT INTO users (username, userid, firstname, lastname, banned, is_spam) VALUES('{username}', '{userid}', '{firstname}', '{lastname}', {banned}, {is_spam})",
                  commit=True)
              self.database.query(
                  f"INSERT INTO settings (userid, balance, lang, tokens, ratings) VALUES('{userid}', {balance}, '{lang}', {tokens}, {ratings})",
                  commit=True)
              return True
          return False
      except:
          return False
    
  # Функция провеки пользователя в базе данных
  def CheckUser(self, userid):
    userdata = self.database.query(
      f"SELECT * FROM users WHERE userid={userid}")
    if len(userdata) <= 0:
      return False
    else:
      return True

  # При нажатии на старт или отправки команды /start
  async def process_start_command(self, message: types.Message):
    userid = message.from_user.id
    username = message.from_user.username
    firstname = message.from_user.first_name
    lastname = message.from_user.last_name

    # Если пользователя нету в БД, то  регистрируем его
    if (not self.CheckUser(userid)):
      self.RegisterUser(username, userid, firstname, lastname)
    await message.reply(
      lang['RU_COMMAND_START'].format(bot_name=self.name_bot_command))

  # Функция ответа на команду /pay
  async def pay_command_handler(self, message: types.Message):
    inline_kb = types.InlineKeyboardMarkup()
    inline_btn = types.InlineKeyboardButton(text='🎫 Поддержать проект',
                                            url='https://www.tinkoff.ru/cf/1EQCoywNvN7')
    inline_kb.add(inline_btn)
    await message.answer(
      "Вы можете поддержать проект, нажав на кнопку ниже. Это поможет нам обновлять и улучшать ИИ. С уважением администрация!",
      reply_markup=inline_kb)

  def GetUserSettings(self, userid):
    userdata = self.database.query(
      f"SELECT * FROM settings WHERE userid={userid}")
    if len(userdata) <= 0:
      return {"result": userdata, "error": False}
    else:
      return {"result": userdata, "error": True}
    
  # Функция ответа на команду /info
  async def info_command_handler(self, message: types.Message):
    user_id = message.from_user.id
    settings_user = self.GetUserSettings(user_id)

    if (settings_user["error"]):
      settings_user = settings_user["result"]
    else:
      return

    balance = settings_user["balance"]
    lang = settings_user["lang"]
    tokens = settings_user["tokens"]
    ratings = settings_user ["ratings"]
    text = f"\n\n<b>Ваш ID:</b> {user_id}\n<b>Ваше имя:</b> <code>{message.from_user.username}</code>\n\n<b>Ваш рейтинг:</b> {ratings}\n<b>Осталось токенов:</b> {tokens}\n\n<b>Ваш баланс:</b> {balance}₽"
    await self.bot.send_message(chat_id=message.chat.id,
                                text=text,
                                reply_to_message_id=message.message_id,
                                parse_mode='HTML')
    
  # Функция ответа на команду /help
  async def help_command_handler(self, message: types.Message):
    user_id = message.from_user.id
    settings_user = self.GetUserSettings(user_id)

    if (settings_user["error"]):
      settings_user = settings_user["result"]
    else:
      return
    text = f"🖥 Инструкция по работе с ИИ:\n\nЧто такое ИИ и для чего он нужен?\n\nИскусственный интеллект (ИИ) — это отрасль информатики, которая фокусируется на создании машин, которые могут думать и действовать как люди. Технология искусственного интеллекта использовалась для создания систем, способных решать сложные задачи, понимать естественный язык, распознавать изображения и многое другое.\n\nЧто я умею?\n\nВыполнять множество разных операций. Отвечать на вопросы. При этом я даю более детальные и проработанные ответы, чем обычные виртуальные помощники. Кроме того, в отличие от поисковиков, я не просто копирую подходящий кусок текста, а структурирую ответ согласно вашему запросу. А еще мне можно задать уточняющие вопросы или попросить раскрыть тему подробнее. Создавать текстовый контент. Статьи, стихи, посты для социальных сетей, сценарии к видео, тексты для почтовых рассылок, рассказы на заданную тему и многое другое — для меня не проблема. Делать выжимки из длинных текстов. Если «скормить» мне текст и попросить сделать выжимку (на английском — summarise), то я выдам краткую версию. При этом сохраняется ключевая информация, чтобы смысл текста не потерялся. Анализировать текст. Я могу проанализировать текст (например, можно задать команду: Иванов, perform sentiment analysis) и рассказать о его содержании. При этом я указываю, в каком ключе написан текст, и пересказываю ключевые мысли. Перефразировать текст. Чат можно попросить переписать (на английском — paraphrase) текст другими словами. Сырой результат вряд ли пройдет проверку на антиплагиат, но как основу для дальнейшей доработки его вполне можно использовать. Переводить текст. Его вполне можно использовать вместо онлайн-переводчика, но принципиального скачка в качестве ожидать не стоит. Писать код. Я могу разрабатывать несложные приложения, анализировать чужой код, давать подсказки и переводить с одного языка программирования в другой.Разумеется, сфера применения гораздо шире и ограничивается лишь вашей фантазией и изобретательностью (некоторые даже умудряются на мне зарабатывать или использовать для решения домашних заданий и написания дипломов). Помните, что Иванов — это всего лишь инструмент, и решать, как именно меня использовать, предстоит пользователю. Например, можно попросить меня сгенерировать детальное описание для запроса в Midjourney или другой нейросети для генераций изображений по тексту.\n\nНу что? Начнем? Нажми команду /start"
    await self.bot.send_message(chat_id=message.chat.id,
                                text=text,
                                reply_to_message_id=message.message_id)

  # Функция ответа на сообщение
  async def echo_message(self, message: types.Message):
    message_id = message.message_id
    rq = message.text
    userid = message.from_user.id
    username = message.from_user.username
    firstname = message.from_user.first_name
    lastname = message.from_user.last_name
    if not self.CheckUser(userid):
      self.RegisterUser(username, userid, firstname, lastname)

    me = await self.bot.get_me()
    print(me.username)

      # Анимация "Печатает":
    await self.bot.send_chat_action(chat_id=message.chat.id, action='typing')

    # Ответное сообщение пользователю на реакцию:
    if message.text == 'Ссылка':
        keyboard_markup = types.InlineKeyboardMarkup(row_width=2)
        url_button = types.InlineKeyboardButton(text='ДА', url='https://t.me/IvanovGPTbot')
        delete_button = types.InlineKeyboardButton(text='НЕТ', callback_data='delete')
        keyboard_markup.add(url_button, delete_button)
        await self.bot.send_message(
            chat_id=message.chat.id,
            text='Вы искали ссылку на бота?',
            reply_to_message_id=message.message_id,
            reply_markup=keyboard_markup
        )

    # Ответное сообщение пользователю на реакцию:
    if rq in [
        'Спасибо!', 'Благодарю!', 'Благодарствую!', 'Мерси!',
        'Большое спасибо!', 'Спасибо большое', 'Спасибо', 'Благодарю',
        'Благодарствую', 'Мерси', 'Большое спасибо', 'Спасибо большое',
        'Спасибо большое,', 'Спасибо,', 'Благодарю,', 'Благодарствую,',
        'Мерси,', 'Большое спасибо,', 'Спасибо за ответ', 'Спасибо за ответ!',
        'Спасибо за информацию!', 'Спасибо за информацию.', '+', 'Ок, спасибо',
        'Ок спасибо', 'Ок, срасибо!', 'Ок'
    ]:
        if message.reply_to_message and message.reply_to_message.from_user.username:
            # получаем имя пользователя, отправившего благодарность
            recipient_username = message.reply_to_message.from_user.username
            # получаем id пользователя, которому отправлена благодарность
            recipient_userid = message.reply_to_message.from_user.id
            # формируем текст сообщения с упоминанием пользователя
            text = f"👍 <code>{username}</code> выразил(а) Вам благодарность (+)!"
            # отправляем сообщение с упоминанием пользователя и парсингом HTML
            await self.bot.send_message(
                chat_id=message.chat.id,
                text=text,
                reply_to_message_id=message.reply_to_message.message_id,
                parse_mode='HTML'
            )
            # увеличиваем количество ratings в таблице settings базы данных на 1
            self.database.query(f"UPDATE settings SET ratings=ratings+1 WHERE userid={recipient_userid}", commit=True)
            self.database.query(f"UPDATE settings SET tokens=tokens+0.25 WHERE userid={recipient_userid}", commit=True)
            # выводим сообщение об успешной отправке
            print(f"({username} -> bot): {rq}\n(bot -> {username}): {username} выразил(а) Вам благодарность!")
            return

    # С запросом ключевого слова "Иванов":
    if self.name_bot_command in rq or f'{self.name_bot_command},' in rq:
      generated_text = self.chatgpt.getAnswer(message=rq,
                                              lang="ru",
                                              temperature=0.7,
                                              max_tokens=1000)
      await self.bot.send_message(chat_id=message.chat.id,
                                  text=generated_text["message"],
                                  reply_to_message_id=message_id)
      print(
        f"(@{username} -> bot): {rq}\n(bot -> @{username}): {generated_text['message']}"
      )