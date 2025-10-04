import json
import random
import telebot
from datetime import datetime, timedelta
import threading

# === 1. BOT TOKEN ===
TOKEN = "8359356550:AAFgGm9wxkWddOtBHdj-b44Vd0EjxHSkAG8"  # ← put your bot token here
bot = telebot.TeleBot(TOKEN)

# === 2. LOAD QUESTIONS AND SCORES ===
with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

try:
    with open("scores.json", "r", encoding="utf-8") as f:
        scores = json.load(f)
except FileNotFoundError:
    scores = {}

used_questions = []  # track asked questions

# === 3. SAVE SCORES ===


def save_scores():
    with open("scores.json", "w", encoding="utf-8") as f:
        json.dump(scores, f, indent=4)

# === 4. RANDOM QUESTION (NO REPEAT UNTIL ALL USED) ===


def get_random_question():
    global used_questions
    remaining = [q for q in questions if q["question"] not in used_questions]
    if not remaining:
        used_questions = []  # reset when all asked
        remaining = questions[:]
    q = random.choice(remaining)
    used_questions.append(q["question"])
    return q

# === 5. SEND QUIZ ===


def send_daily_quiz():
    q = get_random_question()
    question = q["question"]
    options = q["options"]
    correct_option_id = q["correct_option_id"]
    rationale = q["rationale"]

    # Store rationale for follow-up message
    current_quiz["question"] = question
    current_quiz["rationale"] = rationale
    current_quiz["correct_option_id"] = correct_option_id

    poll = bot.send_poll(
        chat_id=1108084497,  # ← your chat_id here
        question=question,
        options=options,
        type="quiz",
        correct_option_id=correct_option_id,
        is_anonymous=False
    )
    print(f"✅ Sent quiz: {question}")


# track last quiz info
current_quiz = {"question": None, "rationale": None, "correct_option_id": None}

# === 6. HANDLE POLL ANSWERS ===


@bot.poll_answer_handler()
def handle_poll_answer(pollAnswer):
    user_id = str(pollAnswer.user.id)
    correct_option_id = current_quiz["correct_option_id"]
    rationale = current_quiz["rationale"]

    if pollAnswer.option_ids[0] == correct_option_id:
        scores[user_id] = scores.get(user_id, 0) + 1
        save_scores()
        bot.send_message(
            user_id, f"✅ Correct! Your total score: {scores[user_id]} pts")
    else:
        bot.send_message(user_id, "❌ Incorrect, better luck next time!")

    # send rationale/explanation
    bot.send_message(user_id, f"💡 Explanation: {rationale}")

# === 7. LEADERBOARD ===


@bot.message_handler(commands=["leaderboard"])
def leaderboard(message):
    if not scores:
        bot.reply_to(message, "No scores yet!")
        return
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    text = "🏆 *Top Scorers:*\n\n"
    for i, (user, score) in enumerate(sorted_scores[:10], 1):
        text += f"{i}. {user}: {score} pts\n"
    bot.reply_to(message, text, parse_mode="Markdown")

# === 8. DAILY 8 AM SCHEDULER ===


def schedule_quiz():
    now = datetime.now()
    next_quiz = datetime.combine(
        now.date(), datetime.strptime("08:00", "%H:%M").time())
    if now > next_quiz:
        next_quiz += timedelta(days=1)
    delay = (next_quiz - now).total_seconds()

    def run_and_reschedule():
        send_daily_quiz()
        threading.Timer(86400, run_and_reschedule).start()  # every 24h

    threading.Timer(delay, run_and_reschedule).start()
    print(f"⏰ Next quiz scheduled at {next_quiz.strftime('%Y-%m-%d %H:%M')}")


# === 9. STARTUP ===
schedule_quiz()    # schedule daily at 8 AM
print("🤖 Bot is running...")
bot.infinity_polling()


