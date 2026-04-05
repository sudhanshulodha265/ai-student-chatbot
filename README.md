# 🤖 AI Student Help Chatbot

An AI-powered student assistance chatbot built with Python Flask and PostgreSQL, featuring NLP-based intent detection, real-time conversation, confidence scoring, and a beautiful dark-themed UI. Deployed live on Render.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.x-lightgrey?style=flat-square&logo=flask)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?style=flat-square&logo=postgresql)
![Deployed on Render](https://img.shields.io/badge/Deployed-Render-46E3B7?style=flat-square&logo=render)

---

## 🌐 Live Demo

🔗 ** https://ai-student-chatbot-vxp0.onrender.com/

---

## 📸 Preview

> Dark glassmorphism UI with animated purple gradient background, typing indicators, quick reply buttons, and real-time chat analytics.

---

## ✨ Features

- 🧠 **NLP Intent Engine** — Keyword-based intent matching across 22 trained intents in 6 topic categories
- 💬 **Real-time Chat** — Smooth messaging UI with animated typing indicators
- 📊 **Chat Analytics** — Live sidebar showing total chats, session count, and top topics
- ⚡ **Quick Replies** — One-click suggested questions for common student queries
- 🗃️ **Conversation Logging** — Every chat saved to PostgreSQL with intent tag and confidence score
- 🎨 **Beautiful Dark UI** — Glassmorphism card with animated purple-pink gradient background
- ☁️ **Cloud Deployed** — Live on Render with PostgreSQL database

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3, Flask |
| Database | PostgreSQL (Render), psycopg2 |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| NLP Engine | Custom keyword-based intent matcher |
| Deployment | Render (Web Service + PostgreSQL) |
| Fonts | DM Sans, DM Serif Display (Google Fonts) |

---

## 🗂️ Project Structure
ai-student-chatbot/
├── app.py              ← Flask backend + NLP engine + REST APIs
├── requirements.txt    ← Python dependencies
├── render.yaml         ← Render deployment config
└── templates/
└── index.html      ← Full chat UI (HTML + CSS + JS)
---

## 🧠 How the NLP Works

The chatbot uses a **keyword-based intent matching engine**:

1. User sends a message
2. The engine scans all 22 patterns stored in the database
3. It finds the best matching pattern using substring matching
4. Returns the matched response with a **confidence score** (0.0 – 1.0)
5. Every conversation is logged in the `chat_logs` table

**Topic categories covered:**
- 💰 Fees & Payments
- 📝 Exams & Results
- 🎓 Admissions & Eligibility
- 📚 Library Timings
- 🏠 Hostel & Accommodation
- 💼 Placements & Internships

---

## 🗄️ Database Schema
```sql
-- Stores all trained intents and responses
CREATE TABLE intents (
    id       SERIAL PRIMARY KEY,
    tag      VARCHAR(50),
    pattern  VARCHAR(255),
    response TEXT
);

-- Logs every conversation with metadata
CREATE TABLE chat_logs (
    id              SERIAL PRIMARY KEY,
    user_message    TEXT,
    bot_response    TEXT,
    intent_matched  VARCHAR(50),
    confidence      FLOAT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🚀 Run Locally

### 1. Clone the repo
```bash
git clone https://github.com/sudhanshulodha265/ai-student-chatbot.git
cd ai-student-chatbot
```

### 2. Install dependencies
```bash
pip install flask psycopg2-binary gunicorn
```

### 3. Set environment variable
```bash
# Windows CMD
set DATABASE_URL=postgresql://user:password@localhost:5432/ai_chatbot

# Mac/Linux
export DATABASE_URL=postgresql://user:password@localhost:5432/ai_chatbot
```

### 4. Run the app
```bash
python app.py
```

### 5. Open in browser
http://localhost:5000
---

## ☁️ Deployment (Render)

This project is configured for one-click deployment on Render using `render.yaml`.

1. Fork this repository
2. Connect to [render.com](https://render.com)
3. Create a new **PostgreSQL** database (free plan)
4. Create a new **Web Service** from this repo
5. Add environment variable: `DATABASE_URL` → your PostgreSQL internal URL
6. Deploy — tables are created automatically on first run ✅

---

## 📡 REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Serves the chat UI |
| POST | `/api/chat` | Send a message, get a response |
| GET | `/api/stats` | Total chats + top intent topics |
| GET | `/api/history` | Last 20 conversations |

### Example API call
```json
POST /api/chat
{ "message": "When are the exams?" }

Response:
{
  "response": "Exams are scheduled in the last week of each semester.",
  "intent": "exam",
  "confidence": 0.87
}
```

---

## 👨‍💻 Author

**Sudhanshu Lodha**
B.Tech Computer Science Engineering

[![GitHub](https://img.shields.io/badge/GitHub-sudhanshulodha265-black?style=flat-square&logo=github)](https://github.com/sudhanshulodha265)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
