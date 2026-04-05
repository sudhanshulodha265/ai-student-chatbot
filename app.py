from flask import Flask, jsonify, render_template, request, session
import sqlite3
import re
import random
import os
import openai

app = Flask(__name__)
app.secret_key = "secret123"

# ---------- OPENAI ----------
openai.api_key = os.environ.get("OPENAI_API_KEY")

SYSTEM_PROMPT = """
You are a professional Student Help Assistant.
Speak politely and clearly. Help students with exams, fees, career, stress.
Keep answers short and helpful.
"""

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

# ---------- GREETING ----------
('greeting','hello','Hello! How can I assist you today?'),
('greeting','hi','Hi there! How can I help you?'),
('greeting','hey','Hey! What can I help you with today?'),
('greeting','good morning','Good morning! How can I assist you?'),
('greeting','good evening','Good evening! How can I help you?'),

# ---------- FEES ----------
('fees','fees','The semester fee must be paid before the 15th of every month.'),
('fees','fee','Fees must be paid through the student portal.'),
('fees','fee payment','You can pay fees online via the student portal.'),
('fees','how to pay fees','Fees can be paid online or at accounts office.'),
('fees','payment','Payments are accepted online and offline.'),
('fees','scholarship','Scholarships are available for students with good academic performance.'),
('fees','fee structure','Fee structure depends on your course. Check portal.'),

# ---------- EXAMS ----------
('exam','exam','Exams are held at the end of each semester.'),
('exam','exam dates','Exam dates are announced 2 weeks before exams.'),
('exam','exam schedule','The exam schedule is available on the college website.'),
('exam','when are exams','Exams usually take place at semester end.'),
('exam','result','Results are declared within 3 weeks after exams.'),
('exam','exam result','You can check results on the student portal.'),

# ---------- ADMISSIONS ----------
('admission','admission','Admissions open in May every year.'),
('admission','admissions','Admissions open in May every year.'),
('admission','application','Applications can be submitted online.'),
('admission','apply','You can apply through the college website.'),
('admission','eligibility','Eligibility requires minimum 60% in 12th.'),
('admission','how to apply','Apply online through official website.'),
('admission','admission process','Fill form, submit documents and pay fees.'),

# ---------- LIBRARY ----------
('library','library','Library is open from 8 AM to 8 PM on weekdays.'),
('library','library timings','Library is open from 8 AM to 8 PM on weekdays.'),
('library','library time','Library operates from 8 AM to 8 PM.'),
('library','books','You can borrow up to 3 books for 14 days.'),
('library','borrow books','Students can borrow books from library.'),
('library','library rules','Maintain silence and return books on time.'),
('library','study room','Library provides quiet study spaces.'),

# ---------- HOSTEL ----------
('hostel','hostel','Hostel facilities are available for students.'),
('hostel','hostel facilities','Hostel includes food, WiFi and laundry.'),
('hostel','accommodation','Accommodation includes meals and basic facilities.'),
('hostel','rooms','Rooms are shared and fully furnished.'),
('hostel','hostel fees','Hostel fees depend on room type.'),
('hostel','mess','Mess provides daily meals for students.'),
('hostel','wifi','Hostel provides internet access.'),

# ---------- PLACEMENT ----------
('placement','placement','Placement drives happen between Nov–March.'),
('placement','placements','Top companies visit campus every year.'),
('placement','placement information','Companies like TCS, Infosys, Oracle visit.'),
('placement','job','Students get job opportunities through placement cell.'),
('placement','internship','Internships are available through placement portal.'),
('placement','companies','Top companies visit campus annually.'),
('placement','placement process','Register → Test → Interview → Selection'),

# ---------- MENTAL SUPPORT ----------
('mental','stress','It’s normal to feel stressed. Take breaks and stay consistent.'),
('mental','tension','Try relaxing and managing your study schedule.'),
('mental','pressure','Focus on one step at a time. You’ll do great.'),
('mental','motivation','Stay consistent. Small progress leads to success.'),

# ---------- GOODBYE ----------
('goodbye','bye','Goodbye! Best of luck with your studies!'),
('goodbye','thanks','You’re welcome! Happy to help!'),
('goodbye','thank you','Glad I could help!'),
])
    db.commit()
    db.close()

init_db()

# ---------- NLP ----------
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9 ]', '', text)
    return text.split()

def find_intent(msg, intents):
    msg_words = clean_text(msg)

    best_match = None
    best_score = 0

    for intent in intents:
        pattern_words = clean_text(intent['pattern'])
        score = len(set(msg_words) & set(pattern_words))

        if score > best_score:
            best_score = score
            best_match = intent

    if best_match and best_score > 0:
        confidence = best_score / len(msg_words)
        return best_match['tag'], best_match['response'], round(confidence, 2)

    return "unknown", None, 0.0

# ---------- AI FALLBACK ----------
def ai_response(message):
    try:
        res = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message}
            ]
        )
        return res['choices'][0]['message']['content']
    except:
        return "I'm facing some issue right now. Please try again later."

# ---------- ROUTES ----------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    msg = data.get('message', '').strip()

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM intents")
    intents = cursor.fetchall()

    tag, response, confidence = find_intent(msg, intents)

    # AI fallback
    if tag == "unknown":
        response = ai_response(msg)
        confidence = 0.9

    # save memory
    history = session.get("history", [])
    history.append({"user": msg, "bot": response})
    session["history"] = history[-5:]

    # save log
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

if __name__ == '__main__':
    app.run()