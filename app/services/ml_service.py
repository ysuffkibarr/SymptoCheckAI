import csv
import re
import os
import pickle
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
        result = process.extractOne(sym, known_symptoms, score_cutoff=60)
        if result:
            match, score, _ = result
            mapped.append(match)
    return mapped

class SymptomClassifier:
    def __init__(self, csv_path, model_cache_path="data/model_cache.pkl"):
        self.csv_path = csv_path
        self.model_cache_path = model_cache_path
        self._load_or_train()

    def _load_or_train(self):
        csv_exists = os.path.exists(self.csv_path)
        cache_exists = os.path.exists(self.model_cache_path)

        if not csv_exists and not cache_exists:
            raise FileNotFoundError(f"Veri dosyası bulunamadı: {self.csv_path}")

        if cache_exists and csv_exists:
            csv_mtime = os.path.getmtime(self.csv_path)
            cache_mtime = os.path.getmtime(self.model_cache_path)
            
            if cache_mtime > csv_mtime:
                with open(self.model_cache_path, "rb") as f:
                    cache = pickle.load(f)
                    self.data = cache["data"]
                    self.disease_corpus = cache["disease_corpus"]
                    self.vectorizer = cache["vectorizer"]
                    self.X = cache["X"]
                    self.feature_names = cache["feature_names"]
                return

        self.data = []
        if csv_exists:
            with open(self.csv_path, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    symptoms = []
                    for key, val in row.items():
                        if key and key.startswith("Symptom_") and val and val.strip():
                            symptoms.append(normalize_symptom(val))
                            
                    disease = row.get("Disease")
                    if disease and symptoms:
                        self.data.append({
                            "disease": disease,
                            "symptoms": symptoms
                        })

        self.disease_corpus = [" ".join(d["symptoms"]) for d in self.data]
        self.vectorizer = TfidfVectorizer()
        self.X = self.vectorizer.fit_transform(self.disease_corpus)
        self.feature_names = self.vectorizer.get_feature_names_out() 

        os.makedirs(os.path.dirname(self.model_cache_path), exist_ok=True)
        with open(self.model_cache_path, "wb") as f:
            pickle.dump({
                "data": self.data,
                "disease_corpus": self.disease_corpus,
                "vectorizer": self.vectorizer,
                "X": self.X,
                "feature_names": self.feature_names
            }, f)

    def _get_triage_level(self, disease_name):
        disease_lower = disease_name.lower()
        
        critical_pattern = re.compile(r'\b(attack|stroke|dengue|malaria|typhoid|failure|cancer|tuberculosis|pneumonia|heart)\b')
        low_pattern = re.compile(r'\b(cold|flu|allergy|acne|fungal|hemorrhoids|common)\b')
        
        if critical_pattern.search(disease_lower):
            return {
                "level": "CRITICAL (RED)", 
                "color": "#dc3545", 
                "action": "Immediate medical attention required. Proceed to the nearest Emergency Room."
            }
        elif low_pattern.search(disease_lower):
            return {
                "level": "LOW (GREEN)", 
                "color": "#28a745", 
                "action": "Home care advised. Monitor symptoms and consult a doctor if they worsen."
            }
        else:
            return {
                "level": "MODERATE (YELLOW)", 
                "color": "#ffc107", 
                "action": "Schedule a polyclinic appointment for professional medical evaluation."
            }

    def predict(self, symptom_text, top_n=5):
        user_symptom_list = [s.strip() for s in symptom_text.split(",")]
        all_symptoms = self.get_all_symptoms()
        mapped_symptoms = map_to_known_symptoms(user_symptom_list, all_symptoms)

        if not mapped_symptoms:
            return []

        symptom_text_joined = " ".join(mapped_symptoms)
        user_vec = self.vectorizer.transform([symptom_text_joined])
        similarities = cosine_similarity(user_vec, self.X).flatten()
        
        indexed = list(enumerate(similarities))
        indexed.sort(key=lambda x: x[1], reverse=True)

        seen = set()
        results = []
        for idx, sim in indexed:
            disease = self.data[idx]["disease"]
            if disease not in seen and sim > 0: 
                seen.add(disease)
                
                disease_vec = self.X[idx]
                contributions = user_vec.multiply(disease_vec).toarray()[0]
                
                explanation = {}
                nonzero_indices = contributions.nonzero()[0]
                for f_idx in nonzero_indices:
                    symptom_word = self.feature_names[f_idx]
                    contrib_score = contributions[f_idx]
                    percentage = round((contrib_score / sim) * 100, 1)
                    explanation[symptom_word] = f"%{percentage}"
                
                explanation = dict(sorted(explanation.items(), key=lambda item: float(item[1].strip('%')), reverse=True))
                
                triage_info = self._get_triage_level(disease)

                results.append({
                    "disease": disease,
                    "similarity_score": round(float(sim), 3),
                    "matched_symptoms": mapped_symptoms,
                    "explanation": explanation,
                    "triage": triage_info
                })
            if len(results) >= top_n:
                break

        return results

    def get_all_symptoms(self):
        sym_set = set()
        for d in self.data:
            sym_set.update(d["symptoms"])
        return sorted(list(sym_set))