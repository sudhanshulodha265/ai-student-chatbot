import os
import psycopg2
import psycopg2.extras
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

DATABASE_URL = os.environ.get('DATABASE_URL', None)

def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def init_db():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS intents (
            id SERIAL PRIMARY KEY,
            tag VARCHAR(50) NOT NULL,
            pattern VARCHAR(255) NOT NULL,
            response TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_logs (
            id SERIAL PRIMARY KEY,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            intent_matched VARCHAR(50),
            confidence FLOAT DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM intents")
    count = cursor.fetchone()[0]

    if count == 0:
        intents_data = [
            ('greeting', 'hello', 'Hello! I am your Student Help Assistant. How can I help you today?'),
            ('greeting', 'hi', 'Hi there! How can I assist you?'),
            ('greeting', 'hey', 'Hey! What can I help you with today?'),
            ('fees', 'fee', 'The semester fee is due by the 15th of every month. You can pay online via the student portal.'),
            ('fees', 'payment', 'Fee payments can be made online at the student portal or at the accounts office.'),
            ('fees', 'scholarship', 'Scholarships are available for students with CGPA above 8.0. Apply before the semester starts.'),
            ('exam', 'exam', 'Exams are scheduled in the last week of each semester. Check the notice board for exact dates.'),
            ('exam', 'result', 'Results are published within 3 weeks after exams on the student portal.'),
            ('exam', 'schedule', 'The exam schedule is posted on the college website 2 weeks before exams begin.'),
            ('admission', 'admission', 'Admissions open in May every year. Visit the admissions office or apply online.'),
            ('admission', 'application', 'You can submit your application online on the college website during the admission period.'),
            ('admission', 'eligibility', 'Eligibility criteria vary by program. Generally 60% in 12th standard is required.'),
            ('library', 'library', 'The library is open from 8 AM to 8 PM on weekdays and 9 AM to 5 PM on weekends.'),
            ('library', 'book', 'You can borrow up to 3 books at a time for a period of 14 days from the library.'),
            ('hostel', 'hostel', 'Hostel facilities are available for outstation students. Apply at the start of the academic year.'),
            ('hostel', 'accommodation', 'Accommodation includes meals, Wi-Fi and laundry facilities. Contact the hostel office for fees.'),
            ('placement', 'placement', 'Placement drives are held between November and March. Register on the placement portal.'),
            ('placement', 'job', 'Top companies like TCS, Infosys, Wipro and Oracle visit our campus every year for recruitment.'),
            ('placement', 'internship', 'Internship opportunities are posted on the placement portal. Check regularly for updates.'),
            ('goodbye', 'bye', 'Goodbye! Best of luck with your studies!'),
            ('goodbye', 'thank', 'You are welcome! Feel free to ask if you need anything else.'),
            ('goodbye', 'thanks', 'Happy to help! Come back anytime.')
        ]
        cursor.executemany(
            "INSERT INTO intents (tag, pattern, response) VALUES (%s, %s, %s)",
            intents_data
        )

    db.commit()
    db.close()

def load_intents():
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT tag, pattern, response FROM intents")
    rows = cursor.fetchall()
    db.close()
    return rows

def find_intent(user_message, intents):
    msg = user_message.lower().strip()
    best_tag = None
    best_response = None
    best_score = 0

    for intent in intents:
        pattern = intent['pattern'].lower()
        if pattern in msg:
            score = len(pattern)
            if score > best_score:
                best_score = score
                best_tag = intent['tag']
                best_response = intent['response']

    confidence = min(best_score / max(len(msg), 1), 1.0)
    return best_tag, best_response, round(confidence, 2)

def save_log(user_msg, bot_response, tag, confidence):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO chat_logs
        (user_message, bot_response, intent_matched, confidence)
        VALUES (%s, %s, %s, %s)
    """, (user_msg, bot_response, tag, confidence))
    db.commit()
    db.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({'response': 'Please type a message!', 'intent': None})

    intents = load_intents()
    tag, response, confidence = find_intent(user_message, intents)

    if not response:
        response = "I'm sorry, I didn't understand that. Try asking about fees, exams, admissions, library, hostel or placements!"
        tag = 'unknown'
        confidence = 0.0

    save_log(user_message, response, tag, confidence)

    return jsonify({
        'response': response,
        'intent': tag,
        'confidence': confidence
    })

@app.route('/api/history')
def history():
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("""
        SELECT user_message, bot_response, intent_matched,
               confidence, created_at
        FROM chat_logs
        ORDER BY created_at DESC
        LIMIT 20
    """)
    logs = cursor.fetchall()
    for log in logs:
        log['created_at'] = str(log['created_at'])
    db.close()
    return jsonify(logs)

@app.route('/api/stats')
def stats():
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT COUNT(*) as total FROM chat_logs")
    total = cursor.fetchone()['total']
    cursor.execute("""
        SELECT intent_matched, COUNT(*) as count
        FROM chat_logs
        WHERE intent_matched != 'unknown'
        GROUP BY intent_matched
        ORDER BY count DESC
        LIMIT 5
    """)
    top_intents = cursor.fetchall()
    db.close()
    return jsonify({'total_chats': total, 'top_intents': top_intents})

with app.app_context():
    if DATABASE_URL:
        init_db()

if __name__ == '__main__':
    app.run(debug=True)