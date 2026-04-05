from flask import Flask, jsonify, render_template, request
import sqlite3

app = Flask(__name__)

# ---------- DATABASE ----------
def get_db():
    conn = sqlite3.connect('chatbot.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS intents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tag TEXT,
        pattern TEXT,
        response TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_message TEXT,
        bot_response TEXT,
        intent_matched TEXT,
        confidence REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute("SELECT COUNT(*) FROM intents")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO intents (tag, pattern, response)
            VALUES (?, ?, ?)
        """, [
            ('greeting','hello','Hello! I am your Student Help Assistant. How can I help you today?'),
            ('greeting','hi','Hi there! How can I assist you?'),
            ('fees','fee','The semester fee is due by the 15th of every month.'),
            ('exam','exam','Exams are scheduled at the end of each semester.'),
            ('admission','admission','Admissions open in May every year.'),
            ('placement','placement','Top companies visit campus for placements.')
        ])

    db.commit()
    db.close()

init_db()

# ---------- NLP ----------
def find_intent(msg, intents):
    msg = msg.lower()
    best = None
    score = 0

    for i in intents:
        if i['pattern'] in msg:
            if len(i['pattern']) > score:
                score = len(i['pattern'])
                best = i

    if best:
        confidence = min(score / len(msg), 1.0)
        return best['tag'], best['response'], round(confidence, 2)

    return "unknown", "Sorry, I didn't understand that.", 0.0

# ---------- ROUTES ----------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    msg = data.get('message', '')

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM intents")
    intents = cursor.fetchall()

    tag, response, confidence = find_intent(msg, intents)

    cursor.execute("""
        INSERT INTO chat_logs (user_message, bot_response, intent_matched, confidence)
        VALUES (?, ?, ?, ?)
    """, (msg, response, tag, confidence))

    db.commit()
    db.close()

    return jsonify({
        "response": response,
        "intent": tag,
        "confidence": confidence
    })

@app.route('/api/stats')
def stats():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM chat_logs")
    total = cursor.fetchone()[0]

    cursor.execute("""
        SELECT intent_matched, COUNT(*) as count
        FROM chat_logs
        GROUP BY intent_matched
        ORDER BY count DESC
        LIMIT 5
    """)

    rows = cursor.fetchall()
    top = [{"intent_matched": r[0], "count": r[1]} for r in rows]

    db.close()

    return jsonify({
        "total_chats": total,
        "top_intents": top
    })

# ---------- RUN ----------
if __name__ == '__main__':
    app.run()