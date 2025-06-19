# SymptoCheckAI

SymptoCheckAI is a lightweight web application that predicts possible diseases based on user-entered symptoms. By leveraging TF-IDF vectorization and cosine similarity, it compares symptoms against a curated dataset to provide the most probable disease matches quickly and accurately.

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

In today’s fast-paced world, early and accessible health information is crucial. SymptoCheckAI offers a fast, simple way for users to enter their symptoms and get an idea of possible diseases. This can help users make informed decisions and seek medical advice sooner.

---

## Features

- User-friendly symptom input interface  
- Fast and interpretable disease prediction with similarity scores  
- Detailed matched symptom list per predicted disease  
- Description field for diseases (if available)  
- Backend powered by FastAPI for performance and scalability  
- Simple, clean frontend for ease of use  
- CORS enabled to support cross-origin requests

---

## Tech Stack

- **Python 3.8+**  
- **FastAPI** - backend framework  
- **scikit-learn** - TF-IDF vectorizer & similarity calculations  
- **Uvicorn** - ASGI server  
- **HTML5 / CSS3 / JavaScript** - frontend

---

## Installation & Usage

1. Clone this repository
   
   git clone https://github.com/YusufKibar/SymptoCheckAI.git
   cd SymptoCheckAI
Create and activate a virtual environment (recommended):

  python -m venv venv
  source venv/bin/activate  # Linux/Mac  
  venv\Scripts\activate     # Windows
  
Install dependencies:

  pip install -r requirements.txt
  
Run the application:

  python symptom_classifier.py

Open your browser and go to:

  http://localhost:8000
  API Endpoints
  POST /api/analyze

Input: JSON with "symptoms": "symptom text"

Output: JSON with top predicted diseases, similarity scores, matched symptoms, and descriptions

GET /api/symptoms

Output: JSON list of all symptoms in the dataset

How It Works
The app loads a CSV dataset of diseases and their associated symptoms.

Symptoms for each disease are combined into a text corpus and vectorized using TF-IDF.

When a user inputs symptoms, their text is vectorized and compared to the dataset via cosine similarity.

The system returns the top N diseases with the highest similarity scores, along with matched symptoms and descriptions.

Future Improvements
Implement advanced machine learning or deep learning models for higher accuracy

Expand and clean the symptom and disease dataset for better coverage

Add user authentication for personalized features

Improve frontend UI/UX with modern frameworks (React, Vue, etc.)

Deploy to cloud platforms with containerization (Docker, Kubernetes)

Add multi-language support

Contributing
Contributions are welcome! Feel free to open issues or submit pull requests. Please ensure code style consistency and provide meaningful commit messages.

License
This project is licensed under the MIT License - see the LICENSE file for details.

Contact
Created by Yusuf Kibar

GitHub: ysuffkibarr

Email: ysufkibar96@gmail.com

