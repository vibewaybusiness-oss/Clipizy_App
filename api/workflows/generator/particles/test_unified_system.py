#!/usr/bin/env python3
"""
Test script for the Unified Particle System.
This script verifies that all particle types work correctly.
"""

import os
import sys
from pathlib import Path

# Add the API directory to the Python path
api_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(api_dir))

from processing.music.generator.particles.unified_particle_system import (
    ParticleConfig,
    ParticleType,
    UnifiedParticleSystem,
)


def test_particle_creation():
    """Test creating different particle types"""
    print("🧪 Testing particle system creation...")
    
    # Test all particle types
    for particle_type in ParticleType:
        try:
            system = UnifiedParticleSystem(particle_type=particle_type)
            status = system.get_status()
            print(f"  ✅ {particle_type.value}: {status['particle_count']} particles")
        except Exception as e:
            print(f"  ❌ {particle_type.value}: {e}")
            return False
    
    return True


def test_configuration():
    """Test configuration system"""
    print("\n⚙️ Testing configuration system...")
    
    try:
        # Test custom configuration
        config = ParticleConfig(
            width=640,
            height=360,
            fps=15,
            duration=2.0,
            particle_count=25,
            bass_threshold=0.2,
            particle_colors=[(255, 0, 0), (0, 255, 0)],
            enhanced_mode={
                "active": True,
                "threshold": 0.2,
                "factor": 1.5
            }
        )
        
        system = UnifiedParticleSystem(particle_type=ParticleType.ENHANCED, config=config)
        
        # Test configuration update
        new_config = {
            "particle_count": 50,
            "bass_threshold": 0.4
        }
        system.update_config(new_config)
        
        status = system.get_status()
        assert status['particle_count'] == 50
        assert system.bass_threshold == 0.4
        
        print("  ✅ Configuration system working")
        return True
        
    except Exception as e:
        print(f"  ❌ Configuration test failed: {e}")
        return False


def test_particle_type_switching():
    """Test switching between particle types"""
    print("\n🔄 Testing particle type switching...")
    
    try:
        system = UnifiedParticleSystem(particle_type=ParticleType.ENHANCED)
        
        # Switch to different types
        for particle_type in [ParticleType.SNOW, ParticleType.BOUNCING, ParticleType.ZEN]:
            system.change_particle_type(particle_type)
            assert system.particle_type == particle_type
            print(f"  ✅ Switched to {particle_type.value}")
        
        print("  ✅ Particle type switching working")
        return True
        
    except Exception as e:
        print(f"  ❌ Particle type switching failed: {e}")
        return False


def test_rendering():
    """Test rendering functionality"""
    print("\n🎬 Testing rendering functionality...")
    
    try:
        # Create test output directory
        test_dir = "test_output"
        os.makedirs(test_dir, exist_ok=True)
        os.chdir(test_dir)
        
        # Test basic rendering
        config = ParticleConfig(
            width=320,
            height=240,
            fps=10,
            duration=1.0,
            particle_count=10
        )
        
        system = UnifiedParticleSystem(particle_type=ParticleType.ENHANCED, config=config)
        output_path = "test_render.mp4"
        system.render_particles(output_path)
        
        # Check if file was created
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print(f"  ✅ Rendering successful: {output_path}")
            return True
        else:
            print("  ❌ Rendering failed: No output file")
            return False
            
    except Exception as e:
        print(f"  ❌ Rendering test failed: {e}")
        return False
    finally:
        # Return to original directory
        os.chdir("..")


def test_audio_loading():
    """Test audio loading functionality"""
    print("\n🎵 Testing audio loading...")
    
    try:
        system = UnifiedParticleSystem(particle_type=ParticleType.ENHANCED)
        
        # Test with non-existent file (should not crash)
        system.load_audio("nonexistent.wav")
        print("  ✅ Handles missing audio file gracefully")
        
        # Test with existing audio file if available
        audio_files = ["song.wav", "test.wav", "audio.wav"]
        for audio_file in audio_files:
            if os.path.exists(audio_file):
                system.load_audio(audio_file)
                print(f"  ✅ Loaded audio: {audio_file}")
                break
        else:
            print("  ⚠️ No audio files found for testing")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Audio loading test failed: {e}")
        return False


def test_fastapi_methods():
    """Test FastAPI integration methods"""
    print("\n🚀 Testing FastAPI integration methods...")
    
    try:
        system = UnifiedParticleSystem(particle_type=ParticleType.ENHANCED)
        
        # Test status method
        status = system.get_status()
        assert isinstance(status, dict)
        assert 'particle_type' in status
        assert 'particle_count' in status
        print("  ✅ get_status() working")
        
        # Test configuration update
        system.update_config({"particle_count": 100})
        assert system.particle_count == 100
        print("  ✅ update_config() working")
        
        # Test particle type change
        system.change_particle_type(ParticleType.SNOW)
        assert system.particle_type == ParticleType.SNOW
        print("  ✅ change_particle_type() working")
        
        # Test available types
        types = system.get_available_particle_types()
        assert isinstance(types, list)
        assert len(types) == len(ParticleType)
        print("  ✅ get_available_particle_types() working")
        
        # Test particle type info
        info = system.get_particle_type_info(ParticleType.SNOW)
        assert isinstance(info, dict)
        assert 'name' in info
        assert 'description' in info
        print("  ✅ get_particle_type_info() working")
        
        return True
        
    except Exception as e:
        print(f"  ❌ FastAPI methods test failed: {e}")
        return False


def test_all_particle_types_rendering():
    """Test rendering all particle types"""
    print("\n🎭 Testing all particle types rendering...")
    
    try:
        # Create test output directory
        test_dir = "test_output"
        os.makedirs(test_dir, exist_ok=True)
        os.chdir(test_dir)
        
        # Basic configuration for all types
        config = ParticleConfig(
            width=160,
            height=120,
            fps=5,
            duration=0.5,
            particle_count=5
        )
        
        success_count = 0
        for particle_type in ParticleType:
            try:
                system = UnifiedParticleSystem(particle_type=particle_type, config=config)
                output_path = f"test_{particle_type.value}.mp4"
                system.render_particles(output_path)
                
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    print(f"  ✅ {particle_type.value}: {output_path}")
                    success_count += 1
                else:
                    print(f"  ❌ {particle_type.value}: No output file")
                    
            except Exception as e:
                print(f"  ❌ {particle_type.value}: {e}")
        
        print(f"  📊 Successfully rendered {success_count}/{len(ParticleType)} particle types")
        return success_count == len(ParticleType)
        
    except Exception as e:
        print(f"  ❌ All particle types test failed: {e}")
        return False
    finally:
        # Return to original directory
        os.chdir("..")


def cleanup_test_files():
    """Clean up test files"""
    print("\n🧹 Cleaning up test files...")
    
    test_dir = "test_output"
    if os.path.exists(test_dir):
        import shutil
        shutil.rmtree(test_dir)
        print("  ✅ Test files cleaned up")


def main():
    """Run all tests"""
    print("🧪 Unified Particle System Test Suite")
    print("=" * 50)
    
    tests = [
        test_particle_creation,
        test_configuration,
        test_particle_type_switching,
        test_rendering,
        test_audio_loading,
        test_fastapi_methods,
        test_all_particle_types_rendering
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"  ❌ Test {test.__name__} crashed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The unified particle system is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the output above for details.")
    
    # Cleanup
    cleanup_test_files()
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
