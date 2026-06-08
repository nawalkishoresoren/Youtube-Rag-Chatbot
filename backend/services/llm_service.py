from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel,RunnablePassthrough,RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from backend.utilities.processing import retriever_loader

load_dotenv(override=True)

class LLM_Service:
    def __init__(self):
        self.llm = ChatOpenAI(model = 'gpt-5.4',temperature=0.2)

        self.prompt = PromptTemplate(
            template =
            """
                system, 
                You are an expert AI assistant specializing in analyzing YouTube video transcripts.\n
                Answer the user's question accurately using ONLY the provided transcript context. 
                If the context doesn't contain the answer, politely state that you can't find it in the video.\n\n
                
                Context:\n{context}

                Question:{question}
            """,
            input_variables=['context','question']
        )

        self.parser = StrOutputParser()
    
    def format_docs(self,relevant_chunks)->str:
        print(f"--- DEBUG: Retrieved {len(relevant_chunks)} chunks ---")
        for i, doc in enumerate(relevant_chunks):
            print(f"Chunk {i+1}: {doc.page_content[:200]}...")
        return '\n\n'.join(doc.page_content for doc in relevant_chunks)
    
    def generate_answer(self, query: str, video_id: str) -> str:
        """
        Loads the video's specific retriever, dynamically builds your custom 
        LCEL parallel chain, and returns the final parsed string answer.
        """
        # 1. Load the dynamic retriever for this video
        retriever = retriever_loader(video_id=video_id)
        
        # 2. Build your custom RunnableParallel chain
        parallel_chain = RunnableParallel({
            'context': retriever | RunnableLambda(self.format_docs),
            'question': RunnablePassthrough()
        })
        
        # 3. Assemble the main LCEL pipeline
        main_chain = parallel_chain | self.prompt | self.llm | self.parser
        
        # 4. Invoke the chain and return the answer
        return main_chain.invoke(query)


