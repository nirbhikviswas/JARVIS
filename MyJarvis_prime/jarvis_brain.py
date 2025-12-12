import os
import datetime
from tinydb import TinyDB, Query
import ollama

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "Memory", "database.json")
db = TinyDB(DB_PATH)

def save_interaction(user, ai):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.insert({'time': timestamp, 'user': user, 'ai': ai})

def recall(query):
    User = Query()
    results = db.search(User.user.search(query))
    if results:
        return f"I remember you said: {results[-1]['user']}"
    return ""

def analyze_image(image_path):
    try:
        with open(image_path, "rb") as f:
            img_bytes = f.read()
        response = ollama.generate(model='llava', prompt="Describe this screen.", images=[img_bytes])
        return response['response']
    except:
        return "Visual systems offline."

def think(user_text):
    if "what did i say" in user_text.lower():
        key = user_text.lower().replace("what did i say about", "").strip()
        memory = recall(key)
        if memory: return memory

    history = db.all()[-3:]
    context = ""
    for h in history:
        context += f"User: {h['user']}\nAI: {h['ai']}\n"

    system_prompt = (
        f"You are Jarvis. Context: {context}. "
        "Reply as a human. Be concise."
    )

    try:
        response = ollama.chat(model='dolphin-llama3', messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_text},
        ])
        reply = response['message']['content']
        save_interaction(user_text, reply)
        return reply
    except:
        return "Offline."