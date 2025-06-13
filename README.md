🎵 ChatterboxTTS Production API

Production-ready Text-to-Speech API with voice cloning capabilities using ResembleAI's ChatterboxTTS. Deploy on RunPod with GPU acceleration for high-performance speech synthesis.

🚀 Quick Start on RunPod
Step 1: Launch RunPod Instance
bash
# Use this Docker image for optimal compatibility
runpod/pytorch:2.0.1-py3.10-cuda11.8.0-devel
Step 2: Clone and Setup
bash
# Navigate to workspace
cd /workspace

# Clone your repository
git clone https://github.com/Aparna0112/Chatterbox-TTS.git

# Enter directory
cd Chatterbox-TTS

# Verify files
ls -la

# Clone ChatterboxTTS model
git clone https://github.com/resemble-ai/chatterbox.git

# Install dependencies
pip install -r requirements.txt

# Start the application
python main.py
Step 3: Access Your API
Your API will be available at:

API Base URL: https://[your-pod-id]-8000.proxy.runpod.net
Interactive Docs: https://[your-pod-id]-8000.proxy.runpod.net/docs
API Schema: https://[your-pod-id]-8000.proxy.runpod.net/openapi.json
Example:

https://g1ddmckctxboyt-8000.proxy.runpod.net
https://g1ddmckctxboyt-8000.proxy.runpod.net/docs
📋 API Documentation
🔗 Base URL
https://[your-pod-id]-8000.proxy.runpod.net
🎭 Voice Management Endpoints
List All Voices
http
GET /voices
Response:

json
{
  "voices": [
    {
      "voice_id": "female_default",
      "name": "Female Default",
      "description": "Professional female voice",
      "type": "builtin",
      "created_at": "2024-01-01T00:00:00Z"
    },
    {
      "voice_id": "voice_1705123456_abc123",
      "name": "John Doe",
      "description": "Custom male voice",
      "type": "custom",
      "created_at": "2024-01-13T12:30:45Z",
      "audio_duration": 15.2
    }
  ],
  "total": 2,
  "builtin": 1,
  "custom": 1
}
Create New Voice
http
POST /voices
Content-Type: multipart/form-data
Parameters:

voice_name (string, required): Name for the new voice
voice_description (string, optional): Description of the voice
audio_file (file, required): Audio sample (WAV/MP3/FLAC, 5-30 seconds)
cURL Example:

bash
curl -X POST "https://[your-pod-id]-8000.proxy.runpod.net/voices" \
  -F "voice_name=John Doe" \
  -F "voice_description=Professional male voice" \
  -F "audio_file=@voice_sample.wav"
Response:

json
{
  "success": true,
  "voice_id": "voice_1705123456_abc123",
  "message": "Voice 'John Doe' created successfully",
  "voice_info": {
    "voice_id": "voice_1705123456_abc123",
    "name": "John Doe",
    "description": "Professional male voice",
    "type": "custom",
    "created_at": "2024-01-13T12:30:45Z",
    "audio_duration": 15.2
  }
}
Delete Voice
http
DELETE /voices/{voice_id}
cURL Example:

bash
curl -X DELETE "https://[your-pod-id]-8000.proxy.runpod.net/voices/voice_1705123456_abc123"
Response:

json
{
  "success": true,
  "message": "Voice 'John Doe' deleted successfully"
}
🎵 Speech Synthesis Endpoints
Generate Speech
http
POST /synthesize
Content-Type: application/json
Request Body:

json
{
  "text": "Hello, this is a test of voice cloning technology!",
  "voice_id": "voice_1705123456_abc123",
  "exaggeration": 0.5,
  "temperature": 0.8,
  "cfg_weight": 0.5,
  "seed": 42
}
Parameters:

text (string, required): Text to synthesize (max 500 characters)
voice_id (string, required): ID of voice to use
exaggeration (float, optional): Expressiveness level (0.25-2.0, default: 0.5)
temperature (float, optional): Randomness (0.05-5.0, default: 0.8)
cfg_weight (float, optional): Clarity control (0.2-1.0, default: 0.5)
seed (int, optional): Random seed for reproducibility (default: 0)
cURL Example:

bash
curl -X POST "https://[your-pod-id]-8000.proxy.runpod.net/synthesize" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is a test of voice cloning!",
    "voice_id": "voice_1705123456_abc123",
    "exaggeration": 0.5,
    "temperature": 0.8
  }'
Response:

json
{
  "success": true,
  "audio_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Speech synthesized successfully using voice 'John Doe'",
  "sample_rate": 24000,
  "duration": 3.45
}
Download Generated Audio
http
GET /audio/{audio_id}
cURL Example:

bash
curl "https://[your-pod-id]-8000.proxy.runpod.net/audio/550e8400-e29b-41d4-a716-446655440000" \
  --output generated_speech.wav
Response: Binary audio file (WAV format)

Get Audio Information
http
GET /audio/{audio_id}/info
Response:

json
{
  "path": "/runpod-volume/audio/550e8400-e29b-41d4-a716-446655440000.wav",
  "text": "Hello, this is a test of voice cloning!",
  "voice_id": "voice_1705123456_abc123",
  "voice_name": "John Doe",
  "sample_rate": 24000,
  "duration": 3.45,
  "generated_at": 1705123456.789,
  "generation_time": 2.34
}
List Generated Audio Files
http
GET /audio
Response:

json
{
  "audio_files": [
    {
      "audio_id": "550e8400-e29b-41d4-a716-446655440000",
      "text": "Hello, this is a test of voice cloning!",
      "voice_name": "John Doe",
      "duration": 3.45,
      "generated_at": 1705123456.789
    }
  ],
  "total": 1
}
🔧 System Endpoints
API Status
http
GET /
Response:

json
{
  "service": "ChatterboxTTS Production API",
  "version": "1.0.0",
  "status": "operational",
  "model_loaded": true,
  "device": "cuda",
  "voices_available": 5,
  "endpoints": [
    "GET /voices - List all voices",
    "POST /voices - Create new voice",
    "DELETE /voices/{voice_id} - Delete voice",
    "POST /synthesize - Generate speech",
    "GET /audio/{audio_id} - Download audio"
  ]
}
Health Check
http
GET /health
Response:

json
{
  "status": "healthy",
  "model_loaded": true,
  "device": "cuda",
  "voices_total": 5,
  "timestamp": 1705123456.789
}
🛠️ Advanced Usage
Python Client Example
python
import requests
import json

# Base URL (replace with your RunPod endpoint)
BASE_URL = "https://g1ddmckctxboyt-8000.proxy.runpod.net"

# Create a new voice
def create_voice(voice_name, audio_file_path, description="Custom voice"):
    with open(audio_file_path, 'rb') as f:
        files = {"audio_file": f}
        data = {
            "voice_name": voice_name,
            "voice_description": description
        }
        response = requests.post(f"{BASE_URL}/voices", files=files, data=data)
        return response.json()

# Generate speech
def synthesize_speech(text, voice_id, **kwargs):
    payload = {
        "text": text,
        "voice_id": voice_id,
        **kwargs
    }
    response = requests.post(f"{BASE_URL}/synthesize", json=payload)
    return response.json()

# Download audio
def download_audio(audio_id, output_path):
    response = requests.get(f"{BASE_URL}/audio/{audio_id}")
    with open(output_path, 'wb') as f:
        f.write(response.content)
    return output_path

# Example usage
if __name__ == "__main__":
    # Create voice
    result = create_voice("My Voice", "sample_voice.wav", "My custom voice")
    voice_id = result["voice_id"]
    print(f"Created voice: {voice_id}")
    
    # Generate speech
    speech_result = synthesize_speech(
        "Hello, world! This is my cloned voice.",
        voice_id,
        exaggeration=0.6,
        temperature=0.7
    )
    audio_id = speech_result["audio_id"]
    print(f"Generated audio: {audio_id}")
    
    # Download audio
    download_audio(audio_id, "output_speech.wav")
    print("Audio downloaded: output_speech.wav")
JavaScript/Node.js Example
javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

const BASE_URL = 'https://g1ddmckctxboyt-8000.proxy.runpod.net';

// Create voice
async function createVoice(voiceName, audioFilePath, description = 'Custom voice') {
    const form = new FormData();
    form.append('voice_name', voiceName);
    form.append('voice_description', description);
    form.append('audio_file', fs.createReadStream(audioFilePath));
    
    const response = await axios.post(`${BASE_URL}/voices`, form, {
        headers: form.getHeaders()
    });
    
    return response.data;
}

// Generate speech
async function synthesizeSpeech(text, voiceId, options = {}) {
    const payload = {
        text,
        voice_id: voiceId,
        ...options
    };
    
    const response = await axios.post(`${BASE_URL}/synthesize`, payload);
    return response.data;
}

// Download audio
async function downloadAudio(audioId, outputPath) {
    const response = await axios.get(`${BASE_URL}/audio/${audioId}`, {
        responseType: 'stream'
    });
    
    const writer = fs.createWriteStream(outputPath);
    response.data.pipe(writer);
    
    return new Promise((resolve, reject) => {
        writer.on('finish', resolve);
        writer.on('error', reject);
    });
}

// Example usage
async function main() {
    try {
        // Create voice
        const voiceResult = await createVoice('My Voice', 'sample_voice.wav');
        const voiceId = voiceResult.voice_id;
        console.log(`Created voice: ${voiceId}`);
        
        // Generate speech
        const speechResult = await synthesizeSpeech(
            'Hello, world! This is my cloned voice.',
            voiceId,
            { exaggeration: 0.6, temperature: 0.7 }
        );
        const audioId = speechResult.audio_id;
        console.log(`Generated audio: ${audioId}`);
        
        // Download audio
        await downloadAudio(audioId, 'output_speech.wav');
        console.log('Audio downloaded: output_speech.wav');
        
    } catch (error) {
        console.error('Error:', error.response?.data || error.message);
    }
}

main();
🎚️ Parameter Tuning Guide
Exaggeration (0.25 - 2.0)
0.25-0.4: Subtle, natural speech
0.5: Balanced expressiveness (recommended)
0.6-0.8: More expressive, emotional
0.9-2.0: Highly expressive, dramatic
Temperature (0.05 - 5.0)
0.1-0.3: Very consistent, robotic
0.4-0.8: Natural variation (recommended)
0.9-1.5: More creative, varied
1.6-5.0: Highly unpredictable
CFG Weight (0.2 - 1.0)
0.2-0.4: Faster, less controlled
0.5: Balanced speed/quality (recommended)
0.6-0.8: Higher quality, slower
0.9-1.0: Maximum quality, slowest
📊 Voice Creation Best Practices
Audio Requirements
Duration: 5-30 seconds
Quality: Clear, noise-free recording
Format: WAV (preferred), MP3, or FLAC
Content: Natural conversational speech
Speaker: Single speaker only
Recording Tips
Environment: Quiet room with minimal echo
Microphone: Use a decent USB or headset mic
Speaking: Natural pace, clear pronunciation
Content: Read a paragraph of normal text
Avoid: Background noise, music, multiple speakers
Optimal Settings by Voice Type
json
{
  "professional_narration": {
    "exaggeration": 0.3,
    "temperature": 0.6,
    "cfg_weight": 0.7
  },
  "conversational": {
    "exaggeration": 0.5,
    "temperature": 0.8,
    "cfg_weight": 0.5
  },
  "expressive_character": {
    "exaggeration": 0.8,
    "temperature": 1.0,
    "cfg_weight": 0.4
  }
}
🚨 Error Handling
Common HTTP Status Codes
200: Success
400: Bad Request (invalid parameters)
404: Not Found (voice/audio doesn't exist)
422: Validation Error (invalid data format)
500: Internal Server Error
503: Service Unavailable (model not loaded)
Error Response Format
json
{
  "detail": "Voice 'invalid_voice_id' not found"
}
Validation Errors
json
{
  "detail": [
    {
      "loc": ["body", "text"],
      "msg": "ensure this value has at most 500 characters",
      "type": "value_error.any_str.max_length",
      "ctx": {"limit_value": 500}
    }
  ]
}
🧪 Testing Your API
Automated Test Script
Run the included test script to verify all endpoints:

bash
python test_api.py https://[your-pod-id]-8000.proxy.runpod.net
Quick Health Check
bash
curl https://[your-pod-id]-8000.proxy.runpod.net/health
Interactive Testing
Visit the auto-generated documentation:

https://[your-pod-id]-8000.proxy.runpod.net/docs
📁 Project Structure
Chatterbox-TTS/
├── main.py                 # Main API application
├── requirements.txt        # Python dependencies
├── test_api.py            # API testing script
├── setup_runpod.sh        # RunPod setup automation
├── Dockerfile             # Container configuration
├── README.md              # This documentation
├── .gitignore            # Git ignore patterns
└── chatterbox/           # ChatterboxTTS model (cloned)
    └── ...
⚡ Performance & Scaling
Hardware Recommendations
GPU: NVIDIA RTX 3090/4090 or better
RAM: 16GB+ system memory
VRAM: 8GB+ GPU memory
Storage: 50GB+ SSD space
Optimization Tips
Batch Processing: Process multiple requests together
Voice Caching: Keep frequently used voices in memory
Audio Compression: Use lower sample rates for faster processing
Resource Monitoring: Monitor GPU/CPU usage
Rate Limiting
Consider implementing rate limiting for production:

python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/synthesize")
@limiter.limit("10/minute")
async def synthesize_speech(request: Request, tts_request: TTSRequest):
    # Your synthesis code here
🔒 Security Considerations
Production Deployment
Add API key authentication
Enable HTTPS/TLS encryption
Implement request rate limiting
Validate all file uploads
Monitor for abuse patterns
File Upload Security
Limit file size (max 10MB)
Restrict file types to audio formats
Scan uploads for malware
Use temporary file cleanup
🆘 Troubleshooting
Model Loading Issues
bash
# Check ChatterboxTTS installation
python -c "from chatterbox.src.chatterbox.tts import ChatterboxTTS; print('✅ OK')"

# Verify CUDA availability
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
Out of Memory Errors
Reduce temperature and cfg_weight values
Use shorter text inputs (< 200 characters)
Restart the service to clear GPU memory
Voice Creation Failures
Check audio file format and duration
Ensure clear, single-speaker audio
Verify file is not corrupted
API Connection Issues
bash
# Check if service is running
curl https://[your-pod-id]-8000.proxy.runpod.net/health

# Verify RunPod proxy is active
# Check RunPod dashboard for pod status
📞 Support & Resources
ChatterboxTTS Model: Resemble AI Repository
RunPod Documentation: RunPod Docs
FastAPI Documentation: FastAPI Docs
Issues: GitHub Issues
📄 License
This project is licensed under the MIT License. The ChatterboxTTS model has its own license terms - please refer to the Resemble AI repository for model-specific licensing.

Made with ❤️ for the AI community

