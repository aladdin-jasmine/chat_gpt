from sentence_transformers import SentenceTransformer
import numpy as np

class SelfImprovingMemory:
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.memory_store = []

    async def store_memory(self, content: str):
        embedding = self.embedding_model.encode(content)

        self.memory_store.append({
            'content': content,
            'embedding': embedding.tolist()
        })

        return {'status': 'stored'}

    async def retrieve_similar(self, query: str):
        query_embedding = self.embedding_model.encode(query)

        similarities = []

        for item in self.memory_store:
            similarity = np.dot(query_embedding, item['embedding'])
            similarities.append((similarity, item['content']))

        similarities.sort(reverse=True)

        return similarities[:5]
