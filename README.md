# SymptoCheckAI 🧬

**AI-Powered Clinical Intelligence & Epidemiological Outbreak Detection Platform**

SymptoCheckAI is an advanced, production-ready web application designed to analyze patient symptoms, predict potential diseases using state-of-the-art Medical NLP, and monitor geographical health anomalies in real-time. Built with a high-performance asynchronous architecture and a custom Web Application Firewall (WAF), it ensures both rapid clinical insights and enterprise-grade security.

---

## 🚀 Key Features

### 🧠 Elite Medical NLP Engine
- **PubMedBERT Integration:** Replaces legacy fuzzy-matching with deep semantic search (`pritamdeka/S-PubMedBert-MS-MARCO`).
- **Contextual Understanding:** Translates and normalizes inputs dynamically, understanding complex medical contexts and filtering out non-medical gibberish.
- **Triage Assessment:** Automatically categorizes predictions into Critical (Red) or Moderate (Yellow) triage levels with actionable clinical advice.

### 🌍 Epidemic Outbreak Detection
- **Statistical Anomaly Scanning:** Analyzes the last 30 days of clinical logs directly on the PostgreSQL database to detect sudden spikes in specific diseases by region.
- **Real-Time Heatmap Data:** Generates `CRITICAL_RED` alerts when a disease exceeds historical baseline averages, acting as an early warning system for public health.

### 🛡️ HoneyMind WAF & Security
- **Custom Web Application Firewall:** Actively detects and permanently bans malicious IPs, automated vulnerability scanners (e.g., `sqlmap`, `dirbuster`), and trap-route intruders.
- **Military-Grade Privacy:** All clinical records are encrypted at rest using AES-256 (`cryptography.fernet`) to ensure absolute GDPR/KVKK compliance.
- **IP Anonymization:** Extracts only broad geographic data (City/Country) from IPs before immediately discarding them.

### 💻 Modern & Accessible UI
- **Voice-to-Text Integration:** Hands-free symptom input using the Web Speech API.
- **Clinical PDF Reports:** One-click generation of professional, formatted diagnostic findings.
- **Apple-Inspired Design:** Clean, responsive, and distraction-free user interface.

---

## 🛠️ Tech Stack

- **Backend:** FastAPI (Async), Uvicorn
- **AI / ML:** PyTorch, Sentence-Transformers (`PubMedBERT`)
- **Database:** PostgreSQL, SQLAlchemy (Asyncpg engine)
- **Security:** Cryptography (AES-256), SlowAPI (Rate Limiting), Custom HoneyMind WAF
- **Frontend:** HTML5, CSS3, JavaScript, HTML2PDF

---

## ⚙️ Installation & Usage

### 1. Clone the Repository
git clone https://github.com/ysuffkibarr/SymptoCheckAI.git
cd SymptoCheckAI

### 2. Create a Virtual Environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

### 3. Install Dependencies
pip install -r requirements.txt

### 4. Environment Variables (.env)
Create a `.env` file in the root directory and configure your secure keys and database URL:

AES_SECRET_KEY=your_base64_url_safe_fernet_key_here
SYMPTO_SECRET_KEY=kibar-ai-production-2026
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/symptocheck

### 5. Start the Server
Run the application using the ASGI server:

uvicorn app.main:app --reload

*The application will be available at: http://localhost:8000*

---

## 📡 API Endpoints

- POST /api/analyze - Analyzes user symptoms via PubMedBERT, returns predictions, and logs anonymized geographic data.
- GET /api/epidemic/outbreaks - Triggers the statistical anomaly detection engine and returns active outbreak alerts.
- GET /api/epidemic/logs - Retrieves recent epidemiological records for dashboard mapping.
- GET /api/symptoms - Fetches the comprehensive list of known symptoms from the model vocabulary.

---

## 🔮 Future Roadmap

- [ ] Containerize the application using Docker and docker-compose.
- [ ] Transition from SQLite/Local-CSV to cloud-native vector databases (e.g., Pinecone, Milvus) for multi-million record scaling.
- [ ] Implement a real-time admin dashboard using WebSockets for live epidemic tracking.
- [ ] Integrate external medical APIs for detailed drug interaction and treatment recommendations.

---

## 📝 License
This project is licensed under the MIT License - see the LICENSE file for details.

---
**Developed by Yusuf Kibar** *Bridging Artificial Intelligence, Cybersecurity, and Public Health.*
