from langchain_text_splitters import RecursiveCharacterTextSplitter


class Chunking_Service:
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
                                                            chunk_size = 400,
                                                            chunk_overlap = 200
                                                        )
        
    def chunk_transcripts(self,data):
        chunks = self.splitter.split_text(data);
        print(len(chunks))
        return chunks
