import json
import random
import telebot
from flask import Flask, request

# === 1. BOT TOKEN ===
TOKEN = "8359356550:AAFgGm9wxkWddOtBHdj-b44Vd0EjxHSkAG8"
bot = telebot.TeleBot(TOKEN)

# === 2. LOAD QUESTIONS AND SCORES ===
with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

try:
    with open("scores.json", "r", encoding="utf-8") as f:
        scores = json.load(f)
except FileNotFoundError:
    scores = {}

used_questions = []

# === 3. SAVE SCORES ===
def save_scores():
    with open("scores.json", "w", encoding="utf-8") as f:
        json.dump(scores, f, indent=4)

# === 4. RANDOM QUESTION (NO REPEAT UNTIL ALL USED) ===
def get_random_question():
    global used_questions
    remaining = [q for q in questions if q["question"] not in used_questions]
    if not remaining:
        used_questions = []
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
    rationale = q.get("rationale", "")

    bot.send_poll(
        chat_id=1108084497,  # ← replace with your chat/group ID
        question=question,
        options=options,
        type="quiz",
        correct_option_id=correct_option_id,
        is_anonymous=False
    )

    print(f"✅ Sent quiz: {question}")
    return f"✅ Sent quiz: {question}"

# === 6. Flask app for webhook ===
app = Flask(__name__)

@app.route("/")
def index():
    return "Bot is running!"

@app.route("/send_quiz", methods=["POST"])
def trigger_quiz():
    return send_daily_quiz(), 200

# === 7. Run Flask ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
