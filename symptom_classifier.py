import csv
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import uvicorn

def normalize_symptom(text):
    text = text.lower()
    text = re.sub(r"[_\-]", " ", text)
    text = re.sub(r"[^a-z\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

app = FastAPI(title="Disease Prediction Based on Symptoms")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

class SymptomRequest(BaseModel):
    symptoms: str

class SymptomClassifier:
    def __init__(self, csv_path):
        self.data = []
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                symptoms = []
                for i in range(1, 18):
                    symp = row.get(f"Symptom_{i}")
                    if symp and symp.strip():
                        normalized = normalize_symptom(symp)
                        symptoms.append(normalized)
                disease = row["Disease"]
                if symptoms:
                    self.data.append({
                        "disease": disease,
                        "symptoms": symptoms
                    })

        self.disease_corpus = [" ".join(d["symptoms"]) for d in self.data]
        self.vectorizer = TfidfVectorizer()
        self.X = self.vectorizer.fit_transform(self.disease_corpus)

    def predict(self, symptom_text, top_n=5):
        symptom_text = normalize_symptom(symptom_text)
        user_vec = self.vectorizer.transform([symptom_text])
        similarities = cosine_similarity(user_vec, self.X).flatten()
        indexed = list(enumerate(similarities))
        indexed.sort(key=lambda x: x[1], reverse=True)

        seen = set()
        results = []
        for idx, sim in indexed:
            disease = self.data[idx]["disease"]
            if disease not in seen:
                seen.add(disease)
                results.append({
                    "disease": disease,
                    "similarity": round(float(sim), 3),
                    "matched_symptoms": self.data[idx]["symptoms"]
                })
            if len(results) >= top_n:
                break

        return results

    def get_all_symptoms(self):
        sym_set = set()
        for d in self.data:
            sym_set.update(d["symptoms"])
        return sorted(list(sym_set))

classifier = SymptomClassifier("DiseaseAndSymptoms.csv")

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/analyze")
async def analyze(req: SymptomRequest):
    if not req.symptoms.strip():
        raise HTTPException(status_code=400, detail="Symptoms cannot be empty.")
    return {"results": classifier.predict(req.symptoms)}

@app.get("/api/symptoms")
async def get_symptom_list():
    return {"symptoms": classifier.get_all_symptoms()}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
