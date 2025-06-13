import os
import time
import torch
import random
import numpy as np
import soundfile as sf
import tempfile
import uuid
import logging
import requests
import io
import json
import base64
from typing import Optional, Dict, Any, List
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Device configuration
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
logger.info(f"🚀 Running on device: {DEVICE}")

# Global model variable
MODEL = None
CHATTERBOX_AVAILABLE = False

# Storage directories - RunPod persistent storage
VOICES_DIR = "/runpod-volume/voices" if os.path.exists("/runpod-volume") else "voices"
AUDIO_DIR = "/runpod-volume/audio" if os.path.exists("/runpod-volume") else "audio"

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(VOICES_DIR, exist_ok=True)

logger.info(f"📁 Voices directory: {VOICES_DIR}")
logger.info(f"📁 Audio directory: {AUDIO_DIR}")

# Voice storage
audio_cache = {}
voice_library = {}

# Default/Built-in voices
BUILTIN_VOICES = {
    "female_default": {
        "voice_id": "female_default",
        "name": "Female Default",
        "description": "Professional female voice",
        "audio_url": "https://storage.googleapis.com/chatterbox-demo-samples/prompts/female_shadowheart4.flac",
        "type": "builtin",
        "created_at": "2024-01-01T00:00:00Z"
    },
    "male_professional": {
        "voice_id": "male_professional", 
        "name": "Male Professional",
        "description": "Confident male voice",
        "audio_url": "https://storage.googleapis.com/chatterbox-demo-samples/prompts/male_professional.flac",
        "type": "builtin",
        "created_at": "2024-01-01T00:00:00Z"
    }
}

# Pydantic models for API
class TTSRequest(BaseModel):
    text: str
    voice_id: Optional[str] = "female_default"
    exaggeration: Optional[float] = 0.5
    temperature: Optional[float] = 0.8
    cfg_weight: Optional[float] = 0.5
    seed: Optional[int] = 0

class VoiceCreateRequest(BaseModel):
    voice_name: str
    voice_description: Optional[str] = "Custom voice"

class VoiceInfo(BaseModel):
    voice_id: str
    name: str
    description: str
    type: str
    created_at: str
    audio_duration: Optional[float] = None

class TTSResponse(BaseModel):
    success: bool
    audio_id: Optional[str] = None
    message: str
    sample_rate: Optional[int] = None
    duration: Optional[float] = None

class VoiceResponse(BaseModel):
    success: bool
    voice_id: Optional[str] = None
    message: str
    voice_info: Optional[VoiceInfo] = None

class VoiceListResponse(BaseModel):
    voices: List[VoiceInfo]
    total: int
    builtin: int
    custom: int

def encode_audio_to_base64(audio_data, sample_rate):
    """Encode audio data to base64 string for storage"""
    try:
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        sf.write(temp_file.name, audio_data, sample_rate)
        
        with open(temp_file.name, 'rb') as f:
            audio_bytes = f.read()
        
        os.unlink(temp_file.name)
        return base64.b64encode(audio_bytes).decode('utf-8')
    except Exception as e:
        logger.error(f"Error encoding audio: {e}")
        return None

def decode_audio_from_base64(base64_string):
    """Decode base64 string back to audio file"""
    try:
        audio_bytes = base64.b64decode(base64_string.encode('utf-8'))
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        temp_file.write(audio_bytes)
        temp_file.close()
        return temp_file.name
    except Exception as e:
        logger.error(f"Error decoding audio: {e}")
        return None

def load_voice_library():
    """Load saved custom voices from persistent storage"""
    global voice_library
    voice_library = BUILTIN_VOICES.copy()
    
    voices_json_path = os.path.join(VOICES_DIR, "voices.json")
    
    try:
        if os.path.exists(voices_json_path):
            with open(voices_json_path, 'r', encoding='utf-8') as f:
                custom_voices = json.load(f)
                voice_library.update(custom_voices)
            logger.info(f"✅ Loaded {len(custom_voices)} custom voices from persistent storage")
        else:
            logger.info("📁 No existing voice library found, starting fresh")
            
        total_voices = len(voice_library)
        custom_count = len([v for v in voice_library.values() if v.get("type") == "custom"])
        builtin_count = len([v for v in voice_library.values() if v.get("type") == "builtin"])
        logger.info(f"📚 Voice Library: {total_voices} total ({builtin_count} builtin, {custom_count} custom)")
        
    except Exception as e:
        logger.error(f"❌ Error loading voice library: {e}")
        logger.info("🔄 Starting with builtin voices only")

def save_voice_library():
    """Save custom voices to persistent storage"""
    try:
        custom_voices = {k: v for k, v in voice_library.items() if v.get("type") != "builtin"}
        voices_json_path = os.path.join(VOICES_DIR, "voices.json")
        
        os.makedirs(os.path.dirname(voices_json_path), exist_ok=True)
        
        with open(voices_json_path, 'w', encoding='utf-8') as f:
            json.dump(custom_voices, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Saved {len(custom_voices)} custom voices to persistent storage")
        
    except Exception as e:
        logger.error(f"❌ Error saving voice library: {e}")

def download_audio_from_url(url):
    """Download audio from URL and save to temporary file"""
    try:
        logger.info(f"📥 Downloading reference audio from: {url}")
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        if response.status_code == 200:
            temp_file = tempfile.NamedTemporaryFile(suffix=".flac", delete=False)
            temp_file.write(response.content)
            temp_file.close()
            
            logger.info(f"✅ Audio downloaded to: {temp_file.name}")
            return temp_file.name
        else:
            logger.error(f"❌ HTTP {response.status_code} when downloading audio")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error downloading audio from URL: {e}")
        return None

def get_voice_audio_path(voice_id):
    """Get the audio path for a voice"""
    if voice_id not in voice_library:
        return None
    
    voice_info = voice_library[voice_id]
    
    if voice_info.get("type") == "custom" and "audio_base64" in voice_info:
        temp_path = decode_audio_from_base64(voice_info["audio_base64"])
        if temp_path:
            logger.info(f"✅ Decoded custom voice audio: {voice_info['name']}")
            return temp_path
        else:
            logger.warning(f"⚠️ Failed to decode audio for voice {voice_id}")
            return None
    
    elif voice_info.get("type") == "builtin" and "audio_url" in voice_info:
        return download_audio_from_url(voice_info["audio_url"])
    
    return None

def load_chatterbox_model():
    """Load ChatterboxTTS model"""
    global MODEL, CHATTERBOX_AVAILABLE
    
    try:
        from chatterbox.src.chatterbox.tts import ChatterboxTTS
        logger.info("✅ Found Resemble AI ChatterboxTTS")
        MODEL = ChatterboxTTS.from_pretrained(DEVICE)
        CHATTERBOX_AVAILABLE = True
        return True
    except ImportError as e:
        logger.warning(f"ChatterboxTTS import failed: {e}")
    except Exception as e:
        logger.warning(f"ChatterboxTTS loading failed: {e}")
    
    # Try alternative import paths
    try:
        from chatterbox.tts import ChatterboxTTS
        MODEL = ChatterboxTTS.from_pretrained(DEVICE)
        CHATTERBOX_AVAILABLE = True
        return True
    except:
        pass
    
    try:
        import chatterbox
        if hasattr(chatterbox, 'ChatterboxTTS'):
            MODEL = chatterbox.ChatterboxTTS.from_pretrained(DEVICE)
            CHATTERBOX_AVAILABLE = True
            return True
    except:
        pass
    
    logger.error("❌ Could not load ChatterboxTTS")
    return False

def create_voice_from_audio(audio_file, voice_name, voice_description="Custom voice"):
    """Create a new voice from uploaded audio"""
    try:
        voice_id = f"voice_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        if isinstance(audio_file, tuple):
            sample_rate, audio_data = audio_file
        else:
            audio_data, sample_rate = sf.read(audio_file)
        
        audio_base64 = encode_audio_to_base64(audio_data, sample_rate)
        if audio_base64 is None:
            raise ValueError("Failed to encode audio")
        
        voice_entry = {
            "voice_id": voice_id,
            "name": voice_name,
            "description": voice_description,
            "audio_base64": audio_base64,
            "sample_rate": int(sample_rate),
            "type": "custom",
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "audio_duration": len(audio_data) / sample_rate
        }
        
        voice_library[voice_id] = voice_entry
        save_voice_library()
        
        logger.info(f"✅ Created voice: {voice_name} ({voice_id})")
        return voice_id, voice_entry
        
    except Exception as e:
        logger.error(f"❌ Error creating voice: {e}")
        return None, None

def set_seed(seed: int):
    """Set random seed for reproducibility"""
    torch.manual_seed(seed)
    if DEVICE == "cuda":
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    random.seed(seed)
    np.random.seed(seed)

def generate_tts_audio(text_input, voice_id, exaggeration, temperature, seed_num, cfgw):
    """Generate TTS audio using ChatterboxTTS model"""
    if MODEL is None:
        raise RuntimeError("No TTS model available")
    
    if seed_num != 0:
        set_seed(int(seed_num))
    
    logger.info(f"🎵 Generating audio for: '{text_input[:50]}...'")
    logger.info(f"🎭 Using voice: {voice_id}")
    
    audio_prompt_path = get_voice_audio_path(voice_id)
    temp_audio_file = None
    
    try:
        if audio_prompt_path and (audio_prompt_path.startswith('/tmp/') or 'temp' in audio_prompt_path):
            temp_audio_file = audio_prompt_path
        
        if audio_prompt_path:
            voice_name = voice_library.get(voice_id, {}).get("name", voice_id)
            logger.info(f"✅ Using voice '{voice_name}' audio: {audio_prompt_path}")
        
        wav = MODEL.generate(
            text_input[:300],
            audio_prompt_path=audio_prompt_path,
            exaggeration=exaggeration,
            temperature=temperature,
            cfg_weight=cfgw,
        )
        
        logger.info("✅ Audio generation complete")
        return (MODEL.sr, wav.squeeze(0).numpy())
        
    except Exception as e:
        logger.error(f"❌ Audio generation failed: {e}")
        raise
    finally:
        if temp_audio_file and os.path.exists(temp_audio_file):
            try:
                os.unlink(temp_audio_file)
            except:
                pass

def generate_id():
    """Generate unique ID"""
    return str(uuid.uuid4())

# Load voice library at startup
load_voice_library()

# FastAPI app
app = FastAPI(
    title="ChatterboxTTS Production API",
    description="Production text-to-speech API with voice cloning for RunPod",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize model on startup"""
    logger.info("🚀 Starting ChatterboxTTS API...")
    success = load_chatterbox_model()
    if success:
        if hasattr(MODEL, 'to'):
            MODEL.to(DEVICE)
        logger.info("✅ ChatterboxTTS model loaded successfully")
    else:
        logger.error("❌ Failed to load ChatterboxTTS model")
        raise RuntimeError("ChatterboxTTS model required for production")

@app.get("/")
async def root():
    """API status endpoint"""
    return {
        "service": "ChatterboxTTS Production API",
        "version": "1.0.0",
        "status": "operational" if MODEL else "model_loading",
        "model_loaded": MODEL is not None,
        "device": DEVICE,
        "voices_available": len(voice_library),
        "endpoints": [
            "GET /voices - List all voices",
            "POST /voices - Create new voice",
            "DELETE /voices/{voice_id} - Delete voice",
            "POST /synthesize - Generate speech",
            "GET /audio/{audio_id} - Download audio"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy" if MODEL else "unhealthy",
        "model_loaded": MODEL is not None,
        "device": DEVICE,
        "voices_total": len(voice_library),
        "timestamp": time.time()
    }

@app.get("/voices", response_model=VoiceListResponse)
async def list_voices():
    """List all available voices"""
    voices = []
    for voice_id, voice_info in voice_library.items():
        voices.append(VoiceInfo(
            voice_id=voice_id,
            name=voice_info["name"],
            description=voice_info["description"],
            type=voice_info["type"],
            created_at=voice_info["created_at"],
            audio_duration=voice_info.get("audio_duration")
        ))
    
    return VoiceListResponse(
        voices=voices,
        total=len(voices),
        builtin=len([v for v in voices if v.type == "builtin"]),
        custom=len([v for v in voices if v.type == "custom"])
    )

@app.post("/voices", response_model=VoiceResponse)
async def create_voice(
    voice_name: str,
    voice_description: str = "Custom voice",
    audio_file: UploadFile = File(...)
):
    """Create a new voice from uploaded audio"""
    try:
        if not voice_name.strip():
            raise HTTPException(status_code=400, detail="Voice name cannot be empty")
        
        # Read uploaded file
        audio_data = await audio_file.read()
        
        # Save to temporary file for processing
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        temp_file.write(audio_data)
        temp_file.close()
        
        # Create voice
        voice_id, voice_entry = create_voice_from_audio(
            temp_file.name, 
            voice_name.strip(), 
            voice_description.strip()
        )
        
        # Cleanup temp file
        os.unlink(temp_file.name)
        
        if voice_id:
            return VoiceResponse(
                success=True,
                voice_id=voice_id,
                message=f"Voice '{voice_name}' created successfully",
                voice_info=VoiceInfo(
                    voice_id=voice_entry["voice_id"],
                    name=voice_entry["name"],
                    description=voice_entry["description"],
                    type=voice_entry["type"],
                    created_at=voice_entry["created_at"],
                    audio_duration=voice_entry.get("audio_duration")
                )
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to create voice")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Voice creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Voice creation failed: {str(e)}")

@app.delete("/voices/{voice_id}")
async def delete_voice(voice_id: str):
    """Delete a voice by ID"""
    if voice_id not in voice_library:
        raise HTTPException(status_code=404, detail="Voice not found")
    
    voice_info = voice_library[voice_id]
    
    if voice_info.get("type") == "builtin":
        raise HTTPException(status_code=400, detail="Cannot delete builtin voices")
    
    try:
        voice_name = voice_info["name"]
        del voice_library[voice_id]
        save_voice_library()
        
        logger.info(f"✅ Deleted voice: {voice_name} ({voice_id})")
        
        return {
            "success": True,
            "message": f"Voice '{voice_name}' deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Voice deletion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Voice deletion failed: {str(e)}")

@app.post("/synthesize", response_model=TTSResponse)
async def synthesize_speech(request: TTSRequest):
    """Synthesize speech from text using voice ID"""
    try:
        if MODEL is None:
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if len(request.text) > 500:
            raise HTTPException(status_code=400, detail="Text too long (max 500 characters)")
        
        if request.voice_id not in voice_library:
            raise HTTPException(status_code=404, detail=f"Voice '{request.voice_id}' not found")
        
        start_time = time.time()
        
        # Generate audio
        sample_rate, audio_data = generate_tts_audio(
            request.text,
            request.voice_id,
            request.exaggeration,
            request.temperature,
            request.seed,
            request.cfg_weight
        )
        
        generation_time = time.time() - start_time
        
        # Save audio file
        audio_id = generate_id()
        audio_path = os.path.join(AUDIO_DIR, f"{audio_id}.wav")
        sf.write(audio_path, audio_data, sample_rate)
        
        # Cache audio info
        voice_name = voice_library[request.voice_id]["name"]
        audio_cache[audio_id] = {
            "path": audio_path,
            "text": request.text,
            "voice_id": request.voice_id,
            "voice_name": voice_name,
            "sample_rate": sample_rate,
            "duration": len(audio_data) / sample_rate,
            "generated_at": time.time(),
            "generation_time": generation_time
        }
        
        logger.info(f"✅ Audio generated: {audio_id} ({generation_time:.2f}s) with voice '{voice_name}'")
        
        return TTSResponse(
            success=True,
            audio_id=audio_id,
            message=f"Speech synthesized successfully using voice '{voice_name}'",
            sample_rate=sample_rate,
            duration=len(audio_data) / sample_rate
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Synthesis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Synthesis failed: {str(e)}")

@app.get("/audio/{audio_id}")
async def get_audio(audio_id: str):
    """Download generated audio file"""
    if audio_id not in audio_cache:
        raise HTTPException(status_code=404, detail="Audio not found")
    
    audio_info = audio_cache[audio_id]
    audio_path = audio_info["path"]
    
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail="Audio file not found on disk")
    
    def iterfile():
        with open(audio_path, "rb") as f:
            yield from f
    
    return StreamingResponse(
        iterfile(),
        media_type="audio/wav",
        headers={
            "Content-Disposition": f"attachment; filename=tts_{audio_id}.wav"
        }
    )

@app.get("/audio/{audio_id}/info")
async def get_audio_info(audio_id: str):
    """Get audio file information"""
    if audio_id not in audio_cache:
        raise HTTPException(status_code=404, detail="Audio not found")
    
    return audio_cache[audio_id]

@app.get("/audio")
async def list_audio():
    """List all generated audio files"""
    return {
        "audio_files": [
            {
                "audio_id": audio_id,
                "text": info["text"][:50] + "..." if len(info["text"]) > 50 else info["text"],
                "voice_name": info.get("voice_name", "Unknown"),
                "duration": info["duration"],
                "generated_at": info["generated_at"]
            }
            for audio_id, info in audio_cache.items()
        ],
        "total": len(audio_cache)
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level="info"
    )
