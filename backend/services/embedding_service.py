from pathlib import Path

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

load_dotenv(override=True)

class Embedding_Service():
    def __init__(self, data=None, video_id: str | None = None):
        self.data = data or []
        self.video_id = video_id
        self.embedding_model = OpenAIEmbeddings()
        self.vector_store = None
        self.base_path = Path("vectorstores")

        if self.data:
            documents = [
                Document(page_content=chunk, metadata={"video_id": self.video_id})
                for chunk in self.data
            ]
            self.vector_store = FAISS.from_documents(
                documents=documents,
                embedding=self.embedding_model,
            )
    
    def build_vector_store(self):
        """
        converts each text chunk into a Document
        creates the FAISS index
        stores it in self.vector_store
        """
        if not self.data:
            raise ValueError('No transcripts provided')
        
        try:
            documents = [
                Document(page_content=chunk, metadata={"video_id": self.video_id})
                for chunk in self.data
            ]
            self.vector_store = FAISS.from_documents(
                documents=documents,
                embedding=self.embedding_model,
            )
            return self.vector_store
        except Exception as e:
            print(str(e))
    
    def save_vector_store(self):
        """
        checks that the FAISS index exists
        makes directory with video_id
        saves under vectorstores/<video_id>
        """
        if not self.vector_store:
            raise ValueError('Vector Store not bilt')

        try:
            save_path = self.base_path/self.video_id
            save_path.parent.mkdir(parents=True, exist_ok=True)

            self.vector_store.save_local(str(save_path))

        except Exception as e:
            print(str(e))
        
    def load_vector_store(self):
        if not self.video_id:
            raise ValueError('No video id provided. Please provide video id.')
        
        try:

            load_path = self.base_path/self.video_id

            if not load_path.exists():
                raise ValueError(f'No saved vectors in {load_path} for video Id = {self.video_id}')
            
            self.vector_store = FAISS.load_local(
                folder_path=str(load_path),
                embeddings= self.embedding_model,
                allow_dangerous_deserialization=True
            )

            return self.vector_store
        except Exception as e:
            print(str(e))
    

        

if __name__ == "__main__":
    chunks = []
    video_id = ' '
    es = Embedding_Service(data = chunks,video_id=video_id)
    es.build_vector_store()
    es.save_vector_store()



