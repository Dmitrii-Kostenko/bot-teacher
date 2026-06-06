import os
import json
import random


def load_questions():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_dir, "data", "questions.json")

    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def get_topics(questions):
    return sorted(list(set(q["topic"] for q in questions)))


def get_question(questions, topic=None):

    if topic and topic != "all":
        filtered = [q for q in questions if q["topic"] == topic]
    else:
        filtered = questions

    question = random.choice(filtered)

    options = [
        question["correct"],
        question["wrong1"],
        question["wrong2"],
        question["wrong3"]
    ]

    random.shuffle(options)

    return {
        "topic": question["topic"],
        "question": question["question"],
        "options": options,
        "correct": question["correct"],
        "hint": question.get("hint", "Нет подсказки")
    }