import telebot
from telebot import types
from config import *

bot = telebot.TeleBot(TOKEN)


# Словарь с вопросами и вариантами ответов (ключ — номер вопроса, значение — кортеж: (вопрос, [ответы]))
questions = {
    1: ("Вам больше нравится: a) решать логические задачи, b) создавать визуальные образы, c) работать с людьми?", ["Программист", "Дизайнер", "Учитель"]),
    2: ("Что вас больше привлекает: a) код и алгоритмы, b) композиция и цвета, c) обучение и объяснение?", ["Программист", "Дизайнер", "Учитель"]),
    3: ("Какой тип работы вам ближе: a) сидячая, с компьютером, b) творческая, с элементами искусства, c) активная, с общением?", ["Программист", "Дизайнер", "Учитель"]),
    4: ("Что для вас важнее c работе: a) точность и логика, b) креативность и стиль, c) помощь и развитие других?", ["Программист", "Дизайнер", "Учитель"]),
    5: ("Какая сфера вас больше интересует: a) IT и технологии, b) искусство и дизайн, c) образование и педагогика?", ["Программист", "Дизайнер", "Учитель"])
}

# Веса ответов для каждой профессии (1 — высокий приоритет, 0.5 — средний, 0 — низкий)
weights = {
    "Программист": {"a": 1, "b": 0, "c": 0.5},
    "Дизайнер":     {"a": 0, "b": 1, "c": 0.5},
    "Учитель":     {"a": 0.5, "b": 0, "c": 1}
}


def calculate_result(chat_id, answers):
    scores = {"Программист": 0, "Дизайнер": 0, "Учитель": 0}

    for q_num, ans in answers.items():
        for profession, weight_dict in weights.items():
            scores[profession] += weight_dict[ans]

    # Находим профессию с максимальным баллом
    best_profession = max(scores, key=scores.get)
    bot.send_message(chat_id, f"По результатам теста вам больше всего подходит профессия: **{best_profession}**! 🎉")
    bot.send_message(chat_id, f"Ваши баллы: Программист — {scores['Программист']}, Дизайнер — {scores['Дизайнер']}, Учитель — {scores['Учитель']}")

    if scores['Программист'] > scores['Дизайнер'] and scores['Программист'] > scores['Учитель']:
        bot.send_message(chat_id, f"вам подходит профессия программиста!")
    elif scores['Дизайнер'] > scores['Программист'] and scores['Дизайнер'] > scores['Учитель']:
        bot.send_message(chat_id, f"вам подходит профессия Дизайнера!")
    elif scores['Учитель'] > scores['Дизайнер'] and scores['Учитель'] > scores['Программист']:
        bot.send_message(chat_id, f"вам подходит профессия Учителя!")
    



@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Давайте определим, какая профессия вам подходит. Отвечайте на 5 вопросов.")
    send_question(message.chat.id, 1, {})  # Начинаем с первого вопроса, пустой словарь ответов
    

def send_question(chat_id, question_num, answers):
    if question_num > 5:  # Если все вопросы заданы
        calculate_result(chat_id, answers)
        return

    question, options = questions[question_num]
    keyboard = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton(text=f"a) {options[0]}", callback_data=f"a_{question_num}"),
        types.InlineKeyboardButton(text=f"b) {options[1]}", callback_data=f"b_{question_num}"),
        types.InlineKeyboardButton(text=f"c) {options[2]}", callback_data=f"c_{question_num}")
    ]
    keyboard.add(*buttons)
    bot.send_message(chat_id, question, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    answer, question_num = call.data.split('_')
    chat_id = call.message.chat.id

    # Сохраняем ответ пользователя
    user_answers = {}
    if call.message.json.get('user_answers'):
        user_answers = call.message.json['user_answers']
    user_answers[int(question_num)] = answer

    # Обновляем сообщение с новыми ответами
    bot.answer_callback_query(call.id)
    send_question(chat_id, int(question_num) + 1, user_answers)







bot.polling(none_stop=True)
