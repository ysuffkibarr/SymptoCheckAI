# SymptoCheckAI - Clinical Intelligence Platform

SymptoCheckAI is an advanced, AI-powered medical decision support API and web application. By leveraging machine learning, natural language processing (NLP), and explainable AI (XAI), it analyzes patient symptoms in multiple languages, provides highly accurate disease predictions, and categorizes emergencies using a clinical triage system. 

Built with a scalable, modular architecture, it is designed for integration into HealthTech applications, enterprise hospital systems, and rapid clinical assessments.

---

## Table of Contents

- [Why SymptoCheckAI?](#why-symptocheckai)  
- [Features](#features)  
- [Tech Stack](#tech-stack)  
- [Installation & Usage](#installation--usage)  
- [API Endpoints](#api-endpoints)  
- [How It Works](#how-it-works)  
- [Future Improvements](#future-improvements)  
- [Contributing](#contributing)  
- [License](#license)  
- [Contact](#contact)

---

## Why SymptoCheckAI?

In today’s fast-paced healthcare environment, rapid and interpretable clinical insights are crucial. SymptoCheckAI goes beyond basic prediction by providing **Explainable AI** (showing the mathematical weight of each symptom) and a **Clinical Triage System** to immediately identify critical cases. It effectively bridges the gap between patient symptoms and professional medical evaluation.

---

## Features

- **Multi-Language Support (NLP):** Automatically detects and translates user symptoms from any language to English for high-accuracy processing.
- **Speech-to-Text Integration:** Allows users to input symptoms via voice commands using a modern frontend interface.
- **Clinical Triage System:** Categorizes results into actionable urgency levels: 🔴 CRITICAL, 🟡 MODERATE, or 🟢 STABLE.
- **Explainable AI (XAI):** Provides a transparent breakdown of how much each input symptom impacted the final diagnosis.
- **Enterprise Security & Rate Limiting:** Protected via RapidAPI headers and strict IP-based rate limiting to prevent abuse.
- **PDF Report Generation:** One-click export of clinical findings for patient records.
- **Production-Ready Architecture:** Fully Dockerized and structured modularly for scalable cloud deployments.

---

## Tech Stack

- **Backend:** Python 3.10+, FastAPI, Uvicorn
- **AI & NLP:** scikit-learn (TF-IDF, Cosine Similarity), rapidfuzz, deep-translator
- **Infrastructure:** Docker, Docker Compose, Loguru (Advanced System Monitoring)
- **Frontend:** HTML5, CSS3, JavaScript, Web Speech API, html2pdf.js

---

## Installation & Usage

### Option 1: Using Docker (Recommended for Production)
1. Clone this repository:
   ```bash
   git clone https://github.com/ysuffkibarr/SymptoCheckAI.git
   cd SymptoCheckAI
   ```
2. Start the application using Docker Compose:
   ```bash
   docker-compose up --build -d
   ```
3. Open your browser and go to: `http://localhost:8000`

### Option 2: Local Python Environment
1. Clone the repository and navigate to the directory.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac  
   venv\Scripts ctivate     # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. **Dataset Requirement:** Ensure that the `DiseaseAndSymptoms.csv` file is present in the `data/` directory.
5. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

---

## API Endpoints

### `POST /api/analyze`
Analyzes symptoms and returns predictions, XAI weights, and triage levels.
- **Headers Required:** `x-sympto-key: kibar-ai-production-2026`
- **Body:** `{"symptoms": "severe headache and high fever"}`
- **Output:** JSON containing matched diseases, confidence scores, explanation breakdown, and triage action.

### `GET /api/symptoms`
- **Output:** JSON list of all unique known symptoms available in the system's database.
- **Rate Limit:** 15 requests per minute per IP.

---

## How It Works

1. **Input & NLP:** User inputs symptoms (text or voice) in any language. The system auto-detects and translates them to the base language.
2. **Fuzzy Matching:** Uses `rapidfuzz` to map misspelled or unformatted text to exact medical terminology.
3. **Vectorization:** Symptoms are vectorized using Term Frequency-Inverse Document Frequency (TF-IDF).
4. **Analysis & Triage:** Calculates cosine similarity against the medical dataset. The engine then assigns a clinical triage level based on the severity of the matched condition.
5. **Explainability:** Generates a weight matrix to show the user exactly why a specific disease was predicted.

---

## Future Improvements

- Integrate Redis for high-speed response caching of common symptom combinations.
- Implement PostgreSQL database logging for global symptom mapping and pandemic prediction.
- Upgrade from TF-IDF to Transformer-based models (BioBERT/ClinicalBERT) for 99%+ accuracy.
- Expand the AI pipeline with patient history and demographic parameters.

---

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests. Please ensure code style consistency and provide meaningful commit messages.

---

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

---

## Contact

**Developed by Yusuf Kibar**
- GitHub: [ysuffkibarr](https://github.com/ysuffkibarr)
- Email: ysufkibar96@gmail.com
