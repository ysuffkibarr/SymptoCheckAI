import csv
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rapidfuzz import process

def normalize_symptom(text):
    text = text.lower()
    text = re.sub(r"[_\-]", " ", text)
    text = re.sub(r"[^a-z\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def map_to_known_symptoms(user_symptoms, known_symptoms):
    mapped = []
    for sym in user_symptoms:
        sym = normalize_symptom(sym)
        match, score, _ = process.extractOne(sym, known_symptoms, score_cutoff=60)
        if match:
            mapped.append(match)
    return mapped

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
        user_symptom_list = [s.strip() for s in symptom_text.split(",")]
        all_symptoms = self.get_all_symptoms()
        mapped_symptoms = map_to_known_symptoms(user_symptom_list, all_symptoms)

        if not mapped_symptoms:
            return []

        symptom_text = "".join(mapped_symptoms)
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