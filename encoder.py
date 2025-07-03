import os
import tempfile
import librosa
import soundfile as sf
from fastapi import UploadFile, HTTPException

def convert_to_wav(voice_file):
    filename = voice_file.filename
    file_extension = filename.split('.')[-1].lower()
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}')
    content = voice_file.file.read()
    temp_file.write(content)
    temp_file.close()
    if file_extension == 'wav':
        return temp_file.name, True
    
    wav_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    wav_file.close()
    
    audio, sample_rate = librosa.load(temp_file.name, sr=None)
    sf.write(wav_file.name, audio, sample_rate, format='WAV')
    
    os.unlink(temp_file.name)
    return wav_file.name, True

def convert_file_path_to_wav(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    file_extension = file_path.split('.')[-1].lower()
    allowed_extensions = ['ogg', 'wav', 'mp3', 'flac', 'm4a', 'aac']
    
    if file_extension not in allowed_extensions:
        raise ValueError(f"File type '{file_extension}' not supported. Allowed: {allowed_extensions}")
    
    if file_extension == 'wav':
        print(f"File is already WAV: {file_path}")
        return file_path, False
    print(f"🔄 Converting {file_extension.upper()} to WAV: {file_path}")
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_wav:
            temp_wav_path = temp_wav.name
        
        audio, sample_rate = librosa.load(file_path, sr=None)
        sf.write(temp_wav_path, audio, sample_rate, format='WAV', subtype='PCM_16')
        
        print(f"✅ Conversion successful: Duration {len(audio)/sample_rate:.2f}s")
        return temp_wav_path, True 
    except Exception as e:
        raise Exception(f"Audio conversion failed: {str(e)}")