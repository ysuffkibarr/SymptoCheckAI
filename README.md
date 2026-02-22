# SymptoCheckAI

SymptoCheckAI is a lightweight web application that predicts possible diseases based on user-entered symptoms. By leveraging fuzzy string matching, TF-IDF vectorization, and cosine similarity, it compares user inputs against a curated dataset to provide the most probable disease matches quickly and accurately.

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
- Intelligent typo tolerance and symptom mapping using fuzzy matching  
- Fast and interpretable disease prediction with similarity scores  
- Detailed matched symptom list per predicted disease  
- Backend powered by FastAPI for performance and scalability  
- Simple, clean frontend for ease of use  
- CORS enabled to support cross-origin requests

---

## Tech Stack

- **Python 3.8+** - **FastAPI** - Backend framework  
- **scikit-learn** - TF-IDF vectorizer & cosine similarity calculations  
- **rapidfuzz** - Advanced string matching for typo-tolerant symptom mapping
- **Uvicorn** - ASGI server  
- **HTML5 / CSS3 / JavaScript** - Frontend

---

## Installation & Usage

1. Clone this repository
   
   git clone https://github.com/ysuffkibarr/SymptoCheckAI.git
   cd SymptoCheckAI
   

2. Create and activate a virtual environment (recommended):

   python -m venv venv
   source venv/bin/activate  # Linux/Mac  
   venv\Scripts\activate     # Windows
  
3. Install dependencies:

   pip install -r requirements.txt
  
4. Dataset Requirement: Ensure that the `DiseaseAndSymptoms.csv` file is present in the root directory. The dataset should contain a `Disease` column and up to 17 symptom columns (`Symptom_1` to `Symptom_17`).

5. Run the application:

   python symptom_classifier.py

6. Open your browser and go to:
   http://localhost:8000

---

## API Endpoints

POST /api/analyze
- Input: JSON with "symptoms": "symptom text" (e.g., comma-separated symptoms)
- Output: JSON with top predicted diseases, similarity scores, and the list of matched symptoms from the dataset.

GET /api/symptoms
- Output: JSON list of all unique known symptoms available in the dataset.

---

## How It Works

1. Data Loading: The app loads the `DiseaseAndSymptoms.csv` dataset, extracting the disease names and normalizing up to 17 symptoms per disease.
2. Fuzzy Matching: When a user inputs symptoms, the system uses `rapidfuzz` to map the user's potentially misspelled or unformatted text to the exact known symptoms in the dataset.
3. Vectorization: The mapped symptoms are then vectorized using Term Frequency-Inverse Document Frequency (TF-IDF).
4. Similarity Calculation: The user's symptom vector is compared to the disease corpus using cosine similarity.
5. Results: The system returns the top N diseases with the highest similarity scores, effectively filtering out duplicates and irrelevant data.

---

## Future Improvements

- Implement advanced machine learning or deep learning models for higher accuracy
- Expand and clean the symptom and disease dataset for better coverage
- Add disease descriptions and recommended next steps
- Add user authentication for personalized features
- Improve frontend UI/UX with modern frameworks (React, Vue, etc.)
- Deploy to cloud platforms with containerization (Docker, Kubernetes)
- Add multi-language support

---

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests. Please ensure code style consistency and provide meaningful commit messages.

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Contact

Created by Yusuf Kibar

- GitHub: ysuffkibarr
- Email: ysufkibar96@gmail.com
