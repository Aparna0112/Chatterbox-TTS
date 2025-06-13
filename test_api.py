#!/usr/bin/env python3
"""
Test script for ChatterboxTTS Production API
Usage: python test_api.py [API_URL]
"""

import requests
import json
import time
import sys
import os
from pathlib import Path

# Default API URL (change this to your RunPod endpoint)
DEFAULT_API_URL = "http://localhost:8000"

class ChatterboxAPITester:
    def __init__(self, base_url=DEFAULT_API_URL):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
    def test_health(self):
        """Test health endpoint"""
        print("🏥 Testing health endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
            print(f"   Model loaded: {data['model_loaded']}")
            print(f"   Device: {data['device']}")
            return True
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
    
    def test_list_voices(self):
        """Test listing voices"""
        print("\n🎭 Testing voice listing...")
        try:
            response = self.session.get(f"{self.base_url}/voices")
            response.raise_for_status()
            data = response.json()
            print(f"✅ Found {data['total']} voices")
            print(f"   Builtin: {data['builtin']}")
            print(f"   Custom: {data['custom']}")
            
            for voice in data['voices']:
                print(f"   - {voice['name']} ({voice['type']}) - {voice['description']}")
            
            return data['voices']
        except Exception as e:
            print(f"❌ Voice listing failed: {e}")
            return []
    
    def create_sample_audio(self, filename="test_voice.wav"):
        """Create a sample audio file for testing"""
        try:
            import numpy as np
            import soundfile as sf
            
            # Generate a simple sine wave (test audio)
            duration = 5  # seconds
            sample_rate = 24000
            frequency = 440  # A4 note
            
            t = np.linspace(0, duration, int(sample_rate * duration))
            audio = 0.3 * np.sin(2 * np.pi * frequency * t)
            
            sf.write(filename, audio, sample_rate)
            print(f"📁 Created sample audio: {filename}")
            return filename
        except ImportError:
            print("⚠️ Cannot create sample audio (missing numpy/soundfile)")
            return None
        except Exception as e:
            print(f"❌ Failed to create sample audio: {e}")
            return None
    
    def test_create_voice(self, audio_file=None):
        """Test voice creation"""
        print("\n🎯 Testing voice creation...")
        
        if audio_file is None:
            audio_file = self.create_sample_audio()
        
        if audio_file is None or not os.path.exists(audio_file):
            print("❌ No audio file available for testing")
            return None
        
        try:
            voice_name = f"Test Voice {int(time.time())}"
            voice_description = "Test voice created by API tester"
            
            with open(audio_file, 'rb') as f:
                files = {"audio_file": f}
                data = {
                    "voice_name": voice_name,
                    "voice_description": voice_description
                }
                
                response = self.session.post(f"{self.base_url}/voices", files=files, data=data)
                response.raise_for_status()
                
                result = response.json()
                voice_id = result["voice_id"]
                print(f"✅ Voice created successfully: {voice_id}")
                print(f"   Name: {result['voice_info']['name']}")
                print(f"   Duration: {result['voice_info'].get('audio_duration', 'N/A')}s")
                
                return voice_id
        except Exception as e:
            print(f"❌ Voice creation failed: {e}")
            return None
    
    def test_synthesize_speech(self, voice_id, text="Hello, this is a test of the ChatterboxTTS API!"):
        """Test speech synthesis"""
        print(f"\n🎵 Testing speech synthesis with voice: {voice_id}")
        try:
            payload = {
                "text": text,
                "voice_id": voice_id,
                "exaggeration": 0.5,
                "temperature": 0.8,
                "cfg_weight": 0.5,
                "seed": 42
            }
            
            response = self.session.post(f"{self.base_url}/synthesize", json=payload)
            response.raise_for_status()
            
            result = response.json()
            audio_id = result["audio_id"]
            print(f"✅ Speech synthesized successfully: {audio_id}")
            print(f"   Sample rate: {result['sample_rate']}Hz")
            print(f"   Duration: {result['duration']:.2f}s")
            
            return audio_id
        except Exception as e:
            print(f"❌ Speech synthesis failed: {e}")
            return None
    
    def test_download_audio(self, audio_id, output_file="test_output.wav"):
        """Test audio download"""
        print(f"\n📥 Testing audio download: {audio_id}")
        try:
            response = self.session.get(f"{self.base_url}/audio/{audio_id}")
            response.raise_for_status()
            
            with open(output_file, 'wb') as f:
                f.write(response.content)
            
            file_size = os.path.getsize(output_file)
            print(f"✅ Audio downloaded successfully: {output_file}")
            print(f"   File size: {file_size} bytes")
            
            return output_file
        except Exception as e:
            print(f"❌ Audio download failed: {e}")
            return None
    
    def test_delete_voice(self, voice_id):
        """Test voice deletion"""
        print(f"\n🗑️ Testing voice deletion: {voice_id}")
        try:
            response = self.session.delete(f"{self.base_url}/voices/{voice_id}")
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ Voice deleted successfully: {result['message']}")
            return True
        except Exception as e:
            print(f"❌ Voice deletion failed: {e}")
            return False
    
    def run_full_test(self):
        """Run complete API test suite"""
        print("🚀 Starting ChatterboxTTS API Test Suite")
        print(f"🔗 API URL: {self.base_url}")
        print("=" * 60)
        
        # Test 1: Health check
        if not self.test_health():
            print("❌ Health check failed - stopping tests")
            return False
        
        # Test 2: List voices
        voices = self.test_list_voices()
        if not voices:
            print("❌ No voices available - stopping tests")
            return False
        
        # Test 3: Create voice
        test_voice_id = self.test_create_voice()
        if not test_voice_id:
            print("⚠️ Voice creation failed - using existing voice")
            test_voice_id = voices[0]['voice_id']
        
        # Test 4: Synthesize speech
        audio_id = self.test_synthesize_speech(test_voice_id)
        if not audio_id:
            print("❌ Speech synthesis failed")
            return False
        
        # Test 5: Download audio
        output_file = self.test_download_audio(audio_id)
        if not output_file:
            print("❌ Audio download failed")
            return False
        
        # Test 6: Delete test voice (only if we created it)
        if test_voice_id.startswith("voice_"):
            self.test_delete_voice(test_voice_id)
        
        print("\n" + "=" * 60)
        print("🎉 All tests completed successfully!")
        print(f"📁 Generated audio file: {output_file}")
        return True

def main():
    """Main function"""
    api_url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_API_URL
    
    print("ChatterboxTTS API Tester")
    print("=" * 60)
    
    tester = ChatterboxAPITester(api_url)
    
    if len(sys.argv) > 2 and sys.argv[2] == "--quick":
        # Quick test - just health and voice list
        print("🔬 Running quick test...")
        tester.test_health()
        tester.test_list_voices()
    else:
        # Full test suite
        success = tester.run_full_test()
        if not success:
            sys.exit(1)

if __name__ == "__main__":
    main()
