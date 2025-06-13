#!/bin/bash

# ChatterboxTTS RunPod Setup Script
# This script helps you deploy the API on RunPod

set -e

echo "🚀 ChatterboxTTS RunPod Setup Script"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're running on RunPod
check_runpod_environment() {
    print_status "Checking RunPod environment..."
    
    if [ -d "/runpod-volume" ]; then
        print_status "✅ RunPod volume detected"
        export RUNPOD_VOLUME="/runpod-volume"
    else
        print_warning "⚠️ RunPod volume not found, using local directories"
        mkdir -p voices audio
        export RUNPOD_VOLUME="$(pwd)"
    fi
    
    # Check for GPU
    if command -v nvidia-smi &> /dev/null; then
        print_status "✅ NVIDIA GPU detected"
        nvidia-smi --query-gpu=name --format=csv,noheader
    else
        print_warning "⚠️ No GPU detected, will use CPU"
    fi
}

# Install system dependencies
install_system_deps() {
    print_status "Installing system dependencies..."
    
    # Update package list
    apt-get update
    
    # Install required packages
    apt-get install -y \
        git \
        wget \
        curl \
        build-essential \
        libsndfile1 \
        ffmpeg \
        python3-dev
    
    print_status "✅ System dependencies installed"
}

# Setup Python environment
setup_python_env() {
    print_status "Setting up Python environment..."
    
    # Upgrade pip
    python3 -m pip install --upgrade pip
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        print_status "Installing Python dependencies..."
        pip install -r requirements.txt
    else
        print_error "requirements.txt not found!"
        exit 1
    fi
    
    print_status "✅ Python environment ready"
}

# Test ChatterboxTTS installation
test_chatterbox() {
    print_status "Testing ChatterboxTTS installation..."
    
    python3 -c "
try:
    from chatterbox.src.chatterbox.tts import ChatterboxTTS
    print('✅ ChatterboxTTS imported successfully')
except ImportError as e:
    print(f'❌ ChatterboxTTS import failed: {e}')
    exit(1)
except Exception as e:
    print(f'⚠️ ChatterboxTTS import warning: {e}')
"
}

# Setup directories and permissions
setup_directories() {
    print_status "Setting up directories..."
    
    # Create necessary directories
    mkdir -p "${RUNPOD_VOLUME}/voices"
    mkdir -p "${RUNPOD_VOLUME}/audio"
    mkdir -p "logs"
    
    # Set permissions
    chmod 755 "${RUNPOD_VOLUME}/voices"
    chmod 755 "${RUNPOD_VOLUME}/audio"
    
    print_status "✅ Directories configured"
}

# Create startup script
create_startup_script() {
    print_status "Creating startup script..."
    
    cat > start_api.sh << 'EOF'
#!/bin/bash

# ChatterboxTTS API Startup Script
echo "🚀 Starting ChatterboxTTS API..."

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:/app"
export CUDA_VISIBLE_DEVICES=0

# Start the API
python3 main.py 2>&1 | tee logs/api.log
EOF

    chmod +x start_api.sh
    print_status "✅ Startup script created: start_api.sh"
}

# Run health check
run_health_check() {
    print_status "Running health check..."
    
    # Start API in background
    python3 main.py &
    API_PID=$!
    
    # Wait for API to start
    sleep 10
    
    # Check if API is responding
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_status "✅ API health check passed"
        kill $API_PID
        return 0
    else
        print_error "❌ API health check failed"
        kill $API_PID
        return 1
    fi
}

# Display setup information
show_setup_info() {
    echo ""
    echo "🎉 Setup Complete!"
    echo "=================="
    echo ""
    echo "📁 Directories:"
    echo "   Voices: ${RUNPOD_VOLUME}/voices"
    echo "   Audio:  ${RUNPOD_VOLUME}/audio"
    echo "   Logs:   $(pwd)/logs"
    echo ""
    echo "🚀 To start the API:"
    echo "   ./start_api.sh"
    echo ""
    echo "🔗 API Endpoints:"
    echo "   GET  /voices                 - List voices"
    echo "   POST /voices                 - Create voice"
    echo "   DELETE /voices/{voice_id}    - Delete voice"
    echo "   POST /synthesize             - Generate speech"
    echo "   GET  /audio/{audio_id}       - Download audio"
    echo ""
    echo "🧪 To test the API:"
    echo "   python3 test_api.py"
    echo ""
}

# Main setup function
main() {
    print_status "Starting RunPod setup..."
    
    # Check if running as root (required for apt-get)
    if [ "$EUID" -ne 0 ]; then
        print_error "Please run as root (use sudo)"
        exit 1
    fi
    
    # Run setup steps
    check_runpod_environment
    install_system_deps
    setup_python_env
    test_chatterbox
    setup_directories
    create_startup_script
    
    # Optional health check
    if [ "$1" != "--no-test" ]; then
        print_status "Running health check (use --no-test to skip)..."
        if ! run_health_check; then
            print_warning "Health check failed, but setup is complete"
        fi
    fi
    
    show_setup_info
    print_status "🎉 RunPod setup completed successfully!"
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "ChatterboxTTS RunPod Setup Script"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --no-test      Skip health check test"
        echo ""
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
