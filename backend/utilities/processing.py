from backend.services.chunking_service import Chunking_Service
from backend.services.embedding_service import Embedding_Service
from backend.services.retriever_service import Retriever_Service
def processing_chain(query:str, transcript:str):
    pass


def create_and_save_vector_store(transcript:str, video_id:str):
    #Break into chunks
    try:
        chunks = Chunking_Service().chunk_transcripts(transcript)
    except Exception as e:
        raise RuntimeError(f'Chunking failed: {e}')

    #save into vector store
    try:
        es = Embedding_Service(data = chunks,video_id=video_id)
        es.build_vector_store()
        es.save_vector_store()
    except Exception as e:
        raise RuntimeError(f'Vector store creation fialed: {e}')

def vectorstore_loader(video_id:str):
    try:
        es = Embedding_Service(video_id=video_id)
        vector_store = es.load_vector_store()

        return vector_store
    except Exception as e:
        raise RuntimeError(f'Vector store loading failed: {e}')

def retriever_loader(video_id:str):
    try:
        retriever = Retriever_Service(video_id=video_id)
        return retriever.load_retriever()
    except Exception as e:
        raise RuntimeError(f'Retriever loading failedL {e}')

def get_relevant_chunks(query:str,video_id:str):
    retriever = retriever_loader(video_id)
    return retriever.invoke(query)


