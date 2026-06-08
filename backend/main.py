from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse

from backend.utilities.utility import generate_transcript, get_video_id
from backend.utilities.processing import processing_chain,create_and_save_vector_store,vectorstore_loader,get_relevant_chunks
from backend.models.Input_Request import InputRequest
from backend.services.llm_service import LLM_Service


app = FastAPI()

@app.get('/')
def home():
    return {'message':'This is home page'}

@app.post('/transcript')
def post_transcript(request:InputRequest):
    url = request.url
    video_id = get_video_id(url)

    if not video_id:
        raise HTTPException(
            status_code=400,
            detail = {'error':'Invalid Youtube URL'}
        )
    
    
    transcript = generate_transcript(video_id)
    if not transcript:
        raise HTTPException(
            status_code=404,
            detail = {'error':'No transcripts present in video.'}
        )
    
    return JSONResponse(status_code=200, content={'video_id':video_id,'transcript':transcript})

@app.post('/ask')
def ask_question(request:InputRequest, query:str):
    video_id = get_video_id(request.url)

    if not video_id:
        raise HTTPException(status_code=400, detail={'error':'Invalid Youtube URL'})
    
    try:
        llm_service = LLM_Service()
        answer = llm_service.generate_answer(query=query,video_id=video_id)

        return JSONResponse(
            status_code=200, 
            content={
                "video_id": video_id,
                "query": query,
                "answer": answer
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail={'error':f'Could not load vector store: {e}'})


@app.post('/process_video')
def process_video(request:InputRequest):
    video_id = get_video_id(request.url)

    if not video_id:
        raise HTTPException(status_code=400, detail={'error':'Invalid Youtube URL'})
    
    transcript = generate_transcript(video_id)
    if not transcript:
        raise HTTPException(
            status_code=404,
            detail = {'error':'No transcripts present in video.'})
    
    try:
    
        create_and_save_vector_store(transcript, video_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail={'error':str(e)})

    return JSONResponse(
                        status_code=200, 
                        content={'video_id':video_id,
                                 'message':'Video transcripts loaded successfully'}
                        )