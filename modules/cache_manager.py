# BookAlchemist/modules/cache_manager.py

import json
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class SemanticCache:
    def __init__(self, embedding_model, cache_file='semantic_cache.json', similarity_threshold=0.95):
        self.cache_file = cache_file
        self.embedding_model = embedding_model
        self.similarity_threshold = similarity_threshold
        self.cache = self._load_cache()

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save_cache(self):
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving semantic cache: {e}")

    def get_similar_answer(self, book_id, question):
        if book_id not in self.cache or not self.cache[book_id]:
            return None

        # --- THE REAL FIX IS HERE ---
        # 1. Get the vector as a list from the embedding model.
        new_question_vector_list = self.embedding_model.embed_query(question)
        # 2. Convert this list into a numpy array.
        new_question_vector_np = np.array(new_question_vector_list)
        
        cached_questions = list(self.cache[book_id].keys())
        cached_vectors = np.array([item['vector'] for item in self.cache[book_id].values()])

        # 3. Now that it's a numpy array, we can safely reshape it.
        similarities = cosine_similarity(
            new_question_vector_np.reshape(1, -1),
            cached_vectors
        )[0]

        if np.max(similarities) >= self.similarity_threshold:
            most_similar_index = np.argmax(similarities)
            most_similar_question = cached_questions[most_similar_index]
            
            print(f"--- Semantic Cache Hit! (Similarity: {np.max(similarities):.2f}) ---")
            print(f"    New Question: '{question}'")
            print(f"    Matched with: '{most_similar_question}'")
            
            return self.cache[book_id][most_similar_question]['answer']
        
        return None

    def add_answer(self, book_id, question, answer):
        if book_id not in self.cache:
            self.cache[book_id] = {}

        question_vector = self.embedding_model.embed_query(question)
        
        # This part was already correct. The vector is a list, which is what JSON needs.
        self.cache[book_id][question] = {
            'answer': answer,
            'vector': question_vector 
        }
        self._save_cache()