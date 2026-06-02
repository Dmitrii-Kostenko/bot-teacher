# src/bot_handlers.py
import os
import json
import random

def load_questions():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    questions_path = os.path.join(base_dir, "data", "questions.json")

    with open(questions_path, "r", encoding="utf-8-sig") as f:
        return json.load(f)
    #with open("data/questions.json", "r", encoding="utf-8-sig") as f:
    #    return json.load(f)

def get_question(questions, topic=None):
    if topic:
        filtered = [q for q in questions if q["topic"] == topic]
    else:
        filtered = questions

    question = random.choice(filtered)
    options = [question["correct"], question["wrong1"], question["wrong2"], question["wrong3"]]
    random.shuffle(options)

    return {
        "topic": question["topic"],
        "question": question["question"],
        "options": options,
        "hint": question["hint"],
        "correct": question["correct"]
    }