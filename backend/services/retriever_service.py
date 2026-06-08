from .embedding_service import Embedding_Service

class Retriever_Service(Embedding_Service):
    def __init__(self, query: str | None = None, video_id: str | None = None):
        self.query = query
        super().__init__(video_id=video_id)
        self.load_vector_store()

    def load_retriever(self):
        if self.vector_store is None:
            raise ValueError("Vector store is not initialized. Provide transcript chunks first.")

        return self.vector_store.as_retriever(search_type = 'mmr',search_kwargs = {"k": 10})

    def retrieve(self, k: int = 4):
        retriever = self.load_retriever()
        return retriever.invoke(self.query)

if __name__ == "__main__":
    
    retriever = Retriever_Service(query="What is the video about?")
    results = retriever.retrieve()