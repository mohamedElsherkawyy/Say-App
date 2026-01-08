import os
from fastapi import FastAPI, File, UploadFile
import uvicorn
from Speech_Recognition import process_audio
from encoder import convert_to_wav
from llm import STTRequest, process_stt
# from ocr import process_image_from_bytes
app = FastAPI()

@app.get("/")
def home():
    return {"message": "Say App is a voice assistant that can help you with your expenses and income newwwwww"}

@app.post("/audio")
def upload_audio(voice_file: UploadFile = File(...)):
    wav_file, cleanup_needed = convert_to_wav(voice_file)
    result = process_audio(wav_file)
    if cleanup_needed:
        os.unlink(wav_file)
    response = process_stt(STTRequest(stt_text=result))
    return response

@app.post("/image")
def upload_image(image_file: UploadFile = File(...)):
    image_bytes = image_file.file.read()
    result = process_image_from_bytes(image_bytes)
    response = process_stt(STTRequest(stt_text=result))
    return response

# @app.post("/image")
# def upload_image(image_file: UploadFile = File(...)):
#     image_bytes = image_file.file.read()
#     result = process_image_from_bytes(image_bytes)
#     response = process_stt(STTRequest(stt_text=result))
#     return response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
