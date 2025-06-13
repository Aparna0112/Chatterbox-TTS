# ChatterboxTTS Production API for RunPod

Production-ready Text-to-Speech API with voice cloning using ResembleAI's ChatterboxTTS, optimized for RunPod deployment.

## 🚀 Features

- **Voice Cloning**: Create custom voices from audio samples
- **Persistent Storage**: Voices saved to RunPod volume
- **RESTful API**: Complete CRUD operations for voices
- **High Performance**: GPU-accelerated inference
- **Production Ready**: Health checks, logging, error handling

## 📋 API Endpoints

### Voice Management
- `GET /voices` - List all available voices
- `POST /voices` - Create new voice from audio file
- `DELETE /voices/{voice_id}` - Delete a voice by ID

### Speech Synthesis
- `POST /synthesize` - Generate speech using voice ID
- `GET /audio/{audio_id}` - Download generated audio
- `GET /audio/{audio_id}/info` - Get audio metadata

### System
- `GET /` - API status and documentation
- `GET /health` - Health check endpoint

## 🛠️ RunPod Setup

### 1. Clone Repository
```bash
git clone https://github.com/Aparna0112/Chatterbox-TTS.git
cd Chatterbox-TTS
```

### 2. Deploy on RunPod

#### Option A: Docker Deployment
```bash
# Build Docker image
docker build -t chatterbox-api .

# Run container with GPU support
docker run --gpus all -p 8000:8000 -v /runpod-volume:/runpod-volume chatterbox-api
```

#### Option B: Direct Python
```bash
# Install dependencies
pip install -r requirements.txt

# Run the API
python main.py
```

### 3. RunPod Template Configuration
Create a RunPod template with:
- **Container Image**: `your-dockerhub-username/chatterbox-api`
- **Container Disk**: 20GB+
- **Volume Mount**: `/runpod-volume` (for persistent voice storage)
- **Expose Ports**: `8000`
- **Environment Variables**:
  - `PORT=8000`

## 📖 Usage Examples

### List All Voices
```bash
curl -X GET http://your-runpod-endpoint:8000/voices
```

### Create New Voice
```bash
curl -X POST http://your-runpod-endpoint:8000/voices \
  -F "voice_name=John Doe" \
  -F "voice_description=Professional male voice" \
  -F "audio_file=@voice_sample.wav"
```

### Generate Speech
```bash
curl -X POST http://your-runpod-endpoint:8000/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is a test of voice cloning!",
    "voice_id": "voice_1234567890_abcdef12",
    "exaggeration": 0.5,
    "temperature": 0.8
  }'
```

### Delete Voice
```bash
curl -X DELETE http://your-runpod-endpoint:8000/voices/voice_1234567890_abcdef12
```

## 🔧 Configuration

### Environment Variables
- `PORT`: API port (default: 8000)
- `CUDA_VISIBLE_DEVICES`: GPU selection

### Storage Paths
- **Voices**: `/runpod-volume/voices/`
- **Audio**: `/runpod-volume/audio/`

## 📊 API Response Examples

### Voice Creation Response
```json
{
  "success": true,
  "voice_id": "voice_1234567890_abcdef12",
  "message": "Voice 'John Doe' created successfully",
  "voice_info": {
    "voice_id": "voice_1234567890_abcdef12",
    "name": "John Doe",
    "description": "Professional male voice",
    "type": "custom",
    "created_at": "2024-01-15T10:30:00Z",
    "audio_duration": 15.2
  }
}
```

### Speech Synthesis Response
```json
{
  "success": true,
  "audio_id": "audio_uuid_here",
  "message": "Speech synthesized successfully using voice 'John Doe'",
  "sample_rate": 24000,
  "duration": 3.45
}
```

### Voice List Response
```json
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
      "voice_id": "voice_1234567890_abcdef12",
      "name": "John Doe",
      "description": "Professional male voice",
      "type": "custom",
      "created_at": "2024-01-15T10:30:00Z",
      "audio_duration": 15.2
    }
  ],
  "total": 2,
  "builtin": 1,
  "custom": 1
}
```

## 🧪 Testing the API

### Using curl
```bash
# Health check
curl http://your-runpod-endpoint:8000/health

# List voices
curl http://your-runpod-endpoint:8000/voices

# Create voice
curl -X POST http://your-runpod-endpoint:8000/voices \
  -F "voice_name=Test Voice" \
  -F "voice_description=Test description" \
  -F "audio_file=@sample.wav"

# Synthesize speech
curl -X POST http://your-runpod-endpoint:8000/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "voice_id": "female_default"}'
```

### Using Python
```python
import requests
import json

# API base URL
BASE_URL = "http://your-runpod-endpoint:8000"

# List voices
response = requests.get(f"{BASE_URL}/voices")
voices = response.json()
print(f"Available voices: {len(voices['voices'])}")

# Create new voice
with open("voice_sample.wav", "rb") as f:
    files = {"audio_file": f}
    data = {
        "voice_name": "My Custom Voice",
        "voice_description": "Custom voice description"
    }
    response = requests.post(f"{BASE_URL}/voices", files=files, data=data)
    result = response.json()
    voice_id = result["voice_id"]
    print(f"Created voice: {voice_id}")

# Generate speech
payload = {
    "text": "Hello, this is my custom voice speaking!",
    "voice_id": voice_id,
    "exaggeration": 0.5,
    "temperature": 0.8
}
response = requests.post(f"{BASE_URL}/synthesize", json=payload)
audio_info = response.json()
audio_id = audio_info["audio_id"]

# Download audio
audio_response = requests.get(f"{BASE_URL}/audio/{audio_id}")
with open("generated_speech.wav", "wb") as f:
    f.write(audio_response.content)
print("Audio saved as generated_speech.wav")
```

## 🚨 Troubleshooting

### Common Issues

1. **Model Loading Failed**
   ```bash
   # Check if ChatterboxTTS is properly installed
   python -c "from chatterbox.src.chatterbox.tts import ChatterboxTTS; print('OK')"
   ```

2. **CUDA Out of Memory**
   - Reduce batch size in model config
   - Use smaller models or CPU fallback

3. **Voice Creation Fails**
   - Check audio file format (WAV, MP3, FLAC supported)
   - Ensure audio is 5-30 seconds long
   - Verify clear speech quality

4. **Persistent Storage Issues**
   ```bash
   # Check volume mount
   ls -la /runpod-volume/
   
   # Check permissions
   chmod 777 /runpod-volume/voices
   ```

### Debug Mode
```bash
# Run with debug logging
export PYTHONPATH=/app
python -c "import logging; logging.basicConfig(level=logging.DEBUG)"
python main.py
```

## 📁 Project Structure

```
chatterbox-runpod-api/
├── main.py              # Main API application
├── requirements.txt     # Python dependencies
├── Dockerfile          # Container configuration
├── README.md           # This file
├── .gitignore         # Git ignore patterns
└── examples/          # Usage examples
    ├── test_api.py    # Python API test script
    └── sample_voice.wav # Sample audio file
```

## 🔒 Security Considerations

- **API Authentication**: Add API key authentication for production
- **Rate Limiting**: Implement request rate limiting
- **File Validation**: Validate uploaded audio files
- **Resource Limits**: Set memory and CPU limits

## 📈 Performance Optimization

- **GPU Utilization**: Ensure CUDA is properly configured
- **Batch Processing**: Process multiple requests together
- **Caching**: Cache frequently used voices
- **Async Processing**: Use background tasks for long operations

## 📄 License

This project uses ResembleAI's ChatterboxTTS model. Please refer to their license terms.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## 📞 Support

For issues and support:
- Check the troubleshooting section
- Review RunPod documentation
- Open GitHub issues for bugs
- Check ChatterboxTTS repository for model-specific issues
