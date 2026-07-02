import faiss
import numpy as np
import os
import json
from sentence_transformers import SentenceTransformer
from typing import List, Dict


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")


class VectorStore:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.catalog_path = os.path.join(DATA_DIR, "shl_catalog.json")
        self.index_path = os.path.join(DATA_DIR, "faiss_index")
        self.documents_path = os.path.join(DATA_DIR, "documents.json")
        self.index = None
        self.documents = []
        self._load_or_create_index()

    def _load_or_create_index(self):
        if os.path.exists(self.index_path) and os.path.exists(self.documents_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.documents_path, "r", encoding="utf-8") as f:
                self.documents = json.load(f)
        else:
            self._create_index()

    def _create_index(self):
        if not os.path.exists(self.catalog_path):
            raise FileNotFoundError(f"Catalog file not found: {self.catalog_path}")
        with open(self.catalog_path, "r", encoding="utf-8") as f:
            catalog = json.load(f)
        self.documents = []

        for product in catalog:
            keys_text = ", ".join(product.get("keys", []))
            job_levels_text = ", ".join(product.get("job_levels", []))
            languages_text = ", ".join(product.get("languages", []))
            
            doc_text = (
                f"Name: {product['name']}\n"
                f"Description: {product.get('description', '')}\n"
                f"Keys: {keys_text}\n"
                f"Job Levels: {job_levels_text}\n"
                f"Languages: {languages_text}\n"
                f"Remote: {product.get('remote', '')}\n"
                f"Adaptive: {product.get('adaptive', '')}\n"
                f"Duration: {product.get('duration', '')}"
            )
            self.documents.append({
                "text": doc_text,
                "metadata": product
            })

        if not self.documents:
            raise ValueError("Catalog is empty! Please add data to shl_catalog.json!")

        embeddings = self.model.encode([doc["text"] for doc in self.documents], convert_to_numpy=True)
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)

        faiss.write_index(self.index, self.index_path)
        with open(self.documents_path, "w", encoding="utf-8") as f:
            json.dump(self.documents, f, indent=2, ensure_ascii=False)

    def retrieve(self, query: str, top_k: int = 10) -> List[Dict]:
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(query_embedding, top_k)
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                result = self.documents[idx]["metadata"].copy()
                result["score"] = float(distances[0][i])
                results.append(result)
        return results
