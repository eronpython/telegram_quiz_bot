import os
import json
import random
from flask import Flask, request
import telebot

# === 1. Telegram bot token ===
TOKEN = "8359356550:AAFgGm9wxkWddOtBHdj-b44Vd0EjxHSkAG8"
bot = telebot.TeleBot(TOKEN)

# === 2. Load questions and scores ===
with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

try:
    with open("scores.json", "r", encoding="utf-8") as f:
        scores = json.load(f)
except FileNotFoundError:
    scores = {}

# === 3. Save scores function ===
def save_scores():
    with open("scores.json", "w", encoding="utf-8") as f:
        json.dump(scores, f, indent=4)

# === 4. Pick a random question ===
used_questions = []

def get_random_question():
    global used_questions
    remaining = [q for q in questions if q["question"] not in used_questions]
    if not remaining:
        used_questions = []
        remaining = questions[:]
    q = random.choice(remaining)
    used_questions.append(q["question"])
    return q

# === 5. Send quiz function ===
CHAT_ID = 1108084497  # e.g., 1108084497

def send_quiz():
    q = get_random_question()
    question = q["question"]
    options = q["options"]
    correct_option_id = q["correct_option_id"]
    rationale = q["rationale"]

    # Send quiz as a Telegram poll
    bot.send_poll(
        chat_id=CHAT_ID,
        question=question,
        options=options,
        type="quiz",
        correct_option_id=correct_option_id,
        is_anonymous=False
    )
    return f"Quiz sent: {question}"

# === 6. Flask server ===
app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "Bot is running!"

# Endpoint Make.com can call
@app.route("/send_quiz", methods=["POST"])
def trigger_quiz():
    result = send_quiz()
    return result, 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
