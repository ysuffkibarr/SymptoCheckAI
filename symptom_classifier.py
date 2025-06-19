import csv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import uvicorn

app = FastAPI(title="SymptoCheckAI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_ui():
    return FileResponse("static/index.html")


class SymptomRequest(BaseModel):
    symptoms: str


class SymptomClassifier:
    def __init__(self, csv_path):
        self.data = []
        self.descriptions = {}
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                symptoms = [row[f"Symptom_{i}"].strip().lower() for i in range(1, 18) if row.get(f"Symptom_{i}")]
                disease = row["Disease"]
                if symptoms:
                    self.data.append({"disease": disease, "symptoms": symptoms})
                self.descriptions[disease] = row.get("Description", "")
        self.disease_corpus = [" ".join(d["symptoms"]) for d in self.data]
        self.vectorizer = TfidfVectorizer()
        self.X = self.vectorizer.fit_transform(self.disease_corpus)

    def predict(self, symptom_text, top_n=5):
        symptom_text = symptom_text.lower()
        user_vec = self.vectorizer.transform([symptom_text])
        similarities = cosine_similarity(user_vec, self.X).flatten()
        indexed = sorted(list(enumerate(similarities)), key=lambda x: x[1], reverse=True)

        seen = set()
        results = []
        for idx, sim in indexed:
            disease = self.data[idx]["disease"]
            if disease not in seen:
                seen.add(disease)
                results.append({
                    "disease": disease,
                    "similarity": round(float(sim), 3),
                    "matched_symptoms": self.data[idx]["symptoms"],
                    "description": self.descriptions.get(disease, "")
                })
            if len(results) >= top_n:
                break
        return results


classifier = SymptomClassifier("DiseaseAndSymptoms.csv")

@app.post("/api/analyze")
async def analyze(req: SymptomRequest):
    if not req.symptoms.strip():
        raise HTTPException(status_code=400, detail="Symptom cannot be empty.")
    return {"results": classifier.predict(req.symptoms)}

@app.get("/api/symptoms")
async def get_symptom_list():
    return {"symptoms": classifier.get_all_symptoms()}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
