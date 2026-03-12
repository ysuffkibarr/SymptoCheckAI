import csv
import re
import os
import pickle
import torch
from sentence_transformers import SentenceTransformer, util
from deep_translator import GoogleTranslator
from app.logger import logger

def normalize_text(text):
    text = text.lower()
    text = re.sub(r"[_\-]", " ", text)
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return re.sub(r"\s+", " ", text).strip()

class SymptomClassifier:
    def __init__(self, csv_path, model_cache_path="data/semantic_cache.pkl"):
        self.csv_path = csv_path
        self.model_cache_path = model_cache_path
        
        logger.info("Initializing Elite Medical Engine (V4.1)... Loading PubMedBERT.")
        self.ai_model = SentenceTransformer('pritamdeka/S-PubMedBert-MS-MARCO')
        self._load_or_train()

    def _load_or_train(self):
        csv_exists = os.path.exists(self.csv_path)
        cache_exists = os.path.exists(self.model_cache_path)

        if cache_exists and csv_exists:
            csv_mtime = os.path.getmtime(self.csv_path)
            cache_mtime = os.path.getmtime(self.model_cache_path)
            if cache_mtime > csv_mtime:
                logger.info("Loading medical tensors from cache...")
                with open(self.model_cache_path, "rb") as f:
                    cache = pickle.load(f)
                    self.data = cache["data"]
                    self.disease_corpus = cache["disease_corpus"]
                    self.corpus_embeddings = cache["corpus_embeddings"]
                    self.medical_vocab = cache["medical_vocab"]
                    self.corpus_embeddings = self.corpus_embeddings.to(self.ai_model.device)
                return

        logger.info("Generating Global Semantic Embeddings...")
        self.data = []
        self.medical_vocab = set()
        
        if csv_exists:
            with open(self.csv_path, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    symptoms = []
                    for key, val in row.items():
                        if key and key.startswith("Symptom_") and val and val.strip():
                            clean_sym = normalize_text(val)
                            symptoms.append(clean_sym)
                            
                            for word in clean_sym.split():
                                if len(word) > 3:
                                    self.medical_vocab.add(word[:4])
                                    
                    disease = row.get("Disease")
                    if disease and symptoms:
                        self.data.append({"disease": disease, "symptoms": symptoms})

        self.disease_corpus = [" ".join(d["symptoms"]) for d in self.data]
        self.corpus_embeddings = self.ai_model.encode(self.disease_corpus, convert_to_tensor=True)

        os.makedirs(os.path.dirname(self.model_cache_path), exist_ok=True)
        with open(self.model_cache_path, "wb") as f:
            pickle.dump({
                "data": self.data,
                "disease_corpus": self.disease_corpus,
                "corpus_embeddings": self.corpus_embeddings.cpu(),
                "medical_vocab": self.medical_vocab
            }, f)
        logger.success("Elite medical model ready.")

    def _get_triage_level(self, disease_name):
        disease_lower = disease_name.lower()
        critical_pattern = re.compile(r'\b(attack|stroke|dengue|malaria|typhoid|failure|cancer|tuberculosis|pneumonia|heart)\b')
        if critical_pattern.search(disease_lower):
            return {"level": "CRITICAL (RED)", "color": "#dc3545", "action": "Immediate medical attention required."}
        return {"level": "MODERATE (YELLOW)", "color": "#ffc107", "action": "Schedule a polyclinic appointment."}

    def predict(self, user_symptoms: str, top_n=5):
        if not user_symptoms or len(user_symptoms) < 3:
            return []

        try:
            translated = GoogleTranslator(source='auto', target='en').translate(user_symptoms)
            logger.info(f"Input: '{user_symptoms}' -> Translated: '{translated}'")
        except Exception as e:
            logger.error(f"Translation Error: {e}")
            translated = user_symptoms

        normalized_input = normalize_text(translated)

        input_words = set(w for w in normalized_input.split() if len(w) > 3)
        is_medical = False
        for w in input_words:
            if w[:4] in self.medical_vocab:
                is_medical = True
                break
                
        if not is_medical:
            logger.warning(f"Blocked gibberish/non-medical input: {user_symptoms}")
            return [] 

        input_chunks = [c.strip() for c in re.split(r'\band\b|,|\.', translated) if len(c.strip()) > 2]
        if not input_chunks:
            input_chunks = [translated]
            
        chunk_embeddings = self.ai_model.encode(input_chunks, convert_to_tensor=True)
        query_embedding = self.ai_model.encode(normalized_input, convert_to_tensor=True)
        cos_scores = util.cos_sim(query_embedding, self.corpus_embeddings)[0]
        
        search_pool = torch.topk(cos_scores, k=min(40, len(self.data)))
        results = []
        seen_diseases = set()

        for score, idx in zip(search_pool[0], search_pool[1]):
            sim_score = score.item()
            disease_data = self.data[idx.item()]
            disease_name = disease_data["disease"]

            if disease_name in seen_diseases or sim_score < 0.35:
                continue

            disease_symptoms = disease_data["symptoms"]
            actual_matches = []
            
            for ds in disease_symptoms:
                ds_words = set(ds.split())
                match_found = False

                for chunk in input_chunks:
                    chunk_words = set(normalize_text(chunk).split())

                    if chunk_words.intersection(ds_words):
                        actual_matches.append(ds)
                        match_found = True
                        break
                        
                    for cw in chunk_words:
                        if len(cw) > 4:
                            for dw in ds_words:
                                if len(dw) > 4 and cw[:4] == dw[:4]:
                                    actual_matches.append(ds)
                                    match_found = True
                                    break
                        if match_found: break
                    if match_found: break
                
                if match_found:
                    continue

                ds_emb = self.ai_model.encode(ds, convert_to_tensor=True)
                chunk_sims = util.cos_sim(chunk_embeddings, ds_emb)
                
                if torch.max(chunk_sims).item() > 0.88:
                    actual_matches.append(ds)

            if not actual_matches: 
                continue

            matched_count = len(actual_matches)
            total_symptoms = len(disease_symptoms)
            coverage_ratio = matched_count / total_symptoms

            complexity_factor = 1.0 / (1.0 + (total_symptoms * 0.1)) 

            final_confidence = (sim_score * 0.4) + (coverage_ratio * 0.5) + (complexity_factor * 0.1)
            final_confidence = max(0.1, min(0.99, final_confidence))

            seen_diseases.add(disease_name)
            triage = self._get_triage_level(disease_name)

            results.append({
                "disease": disease_name,
                "similarity_score": round(final_confidence, 3),
                "matched_symptoms": actual_matches,
                "explanation": {
                    "AI Match": f"%{round(sim_score * 100, 1)}",
                    "Coverage": f"{matched_count}/{total_symptoms}",
                    "Penalty Applied": "Yes" if total_symptoms > 4 else "No"
                },
                "triage": triage
            })

        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results[:top_n]

    def get_all_symptoms(self):
        sym_set = set()
        for d in self.data: sym_set.update(d["symptoms"])
        return sorted(list(sym_set))