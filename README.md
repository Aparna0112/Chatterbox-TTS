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
git clone https://github.com/yourusername/chatterbox-runpod-api.git
cd chatterbox-runpod-api
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
    "
