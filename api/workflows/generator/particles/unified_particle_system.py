import math
import os
import shutil
import subprocess
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import cv2
import librosa
import numpy as np


class ParticleType(Enum):
    SNOW = "snow"
    ZEN = "zen"
    ENHANCED = "enhanced"
    BOUNCING = "bouncing"
    CONTINUOUS_SPAWNING = "continuous_spawning"
    NO_MUSIC = "no_music"


@dataclass
class ParticleConfig:
    width: int = 1920
    height: int = 1080
    fps: int = 30
    x_position: float = 0.5
    y_position: float = 0.5
    particle_count: int = 200
    duration: float = 10.0
    bass_threshold: float = 0.3
    outer_movement_strength: float = 2.0
    inner_movement_strength: float = 1.0
    particle_colors: Optional[List[Tuple[int, int, int]]] = None
    speed_x: float = 0
    speed_y: float = 0
    speed_z: float = 0
    bounce: bool = False
    steady_spawn_rate: float = 0.5
    max_particles: int = 1000
    enhanced_mode: Optional[Dict[str, Any]] = None
    spawn_center_x: float = 0.5
    spawn_center_y: float = 0.5
    spawn_area_width: float = 0.0
    spawn_area_height: float = 0.0


class UnifiedParticleSystem:
    """
    Unified particle system that combines all particle types for FastAPI integration:
    - Snow particles with bass-triggered respawning
    - Zen particles with atmospheric effects
    - Enhanced particles with advanced features
    - Bouncing particles with screen boundaries
    - Continuous spawning particles
    - No-music particles for static effects
    """

    def __init__(self, particle_type: ParticleType = ParticleType.ENHANCED, config: Optional[ParticleConfig] = None):
        self.particle_type = particle_type
        self.config = config or ParticleConfig()
        
        # Basic properties
        self.W = self.config.width
        self.H = self.config.height
        self.fps = int(self.config.fps)
        
        # Position
        self.x_pos = float(self.config.x_position)
        self.y_pos = float(self.config.y_position)
        self.cx = int(self.W * self.x_pos)
        self.cy = int(self.H * self.y_pos)
        
        # Particle settings
        self.particle_count = int(self.config.particle_count)
        self.duration = float(self.config.duration)
        
        # Music-dependent settings
        self.bass_threshold = float(self.config.bass_threshold)
        self.outer_movement_strength = float(self.config.outer_movement_strength)
        self.inner_movement_strength = float(self.config.inner_movement_strength)
        
        # Particle appearance and behavior settings
        self.particle_colors = self.config.particle_colors or [(255, 255, 255)]
        self.speed_x = float(self.config.speed_x)
        self.speed_y = float(self.config.speed_y)
        self.speed_z = float(self.config.speed_z)
        self.bounce = bool(self.config.bounce)
        
        # Enhanced mode settings
        self.enhanced_mode = self.config.enhanced_mode or {
            "active": True,
            "threshold": 0.3,
            "factor": 2.0
        }
        
        # Continuous spawning settings
        self.steady_spawn_rate = float(self.config.steady_spawn_rate)
        self.max_particles = int(self.config.max_particles)
        
        # Spawning area settings
        self.spawn_center_x = float(self.config.spawn_center_x)
        self.spawn_center_y = float(self.config.spawn_center_y)
        self.spawn_area_width = float(self.config.spawn_area_width)
        self.spawn_area_height = float(self.config.spawn_area_height)
        
        # Calculate spawning area bounds
        self.spawn_center_px_x = int(self.W * self.spawn_center_x)
        self.spawn_center_px_y = int(self.H * self.spawn_center_y)
        self.spawn_area_px_width = int(self.W * self.spawn_area_width)
        self.spawn_area_px_height = int(self.H * self.spawn_area_height)
        
        # Audio data
        self.audio_data = None
        self.sample_rate = None
        self.bass_frequencies = None
        
        # Pre-allocate black frame
        self.black_frame = np.zeros((self.H, self.W, 3), dtype=np.uint8)
        
        # Particle system
        self.particles = self._init_particles()
        
        # Spawning tracking for continuous spawning
        self.spawn_accumulator = 0.0

    def _init_particles(self):
        """Initialize particle system based on particle type"""
        particles = []
        
        if self.particle_type == ParticleType.SNOW:
            return self._init_snow_particles()
        elif self.particle_type == ParticleType.CONTINUOUS_SPAWNING:
            return []  # Start empty for continuous spawning
        else:
            return self._init_standard_particles()
    
    def _init_snow_particles(self):
        """Initialize snowflake particles with outward movement"""
        particles = []
        for _ in range(self.particle_count):
            x = self.cx
            y = self.cy
            angle = np.random.uniform(0, 2 * np.pi)
            speed = np.random.uniform(0.5, 2.0)
            vx = speed * np.cos(angle)
            vy = speed * np.sin(angle)
            
            particles.append({
                'x': x, 'y': y,
                'vx': vx, 'vy': vy,
                'size': np.random.uniform(1, 4),
                'brightness': np.random.uniform(0.6, 1.0),
                'pulse_phase': np.random.uniform(0, 2 * np.pi),
                'rotation': np.random.uniform(0, 2 * np.pi),
                'rotation_speed': np.random.uniform(-0.1, 0.1),
                'drift_x': np.random.uniform(-0.2, 0.2),
                'drift_y': np.random.uniform(-0.1, 0.1),
                'life': 1.0,
            })
        return particles
    
    def _init_standard_particles(self):
        """Initialize standard particles for most particle types"""
        particles = []
        for _ in range(self.particle_count):
            angle = np.random.uniform(0, 2 * np.pi)
            distance = np.random.uniform(200, 400)
            x = self.cx + distance * np.cos(angle)
            y = self.cy + distance * np.sin(angle)
            
            # Speed initialization
            vx = np.random.uniform(-0.5, 0.5) if self.speed_x == 0 else self.speed_x
            vy = np.random.uniform(-0.5, 0.5) if self.speed_y == 0 else self.speed_y
            vz = np.random.uniform(-0.1, 0.1) if self.speed_z == 0 else self.speed_z
            
            # Color selection
            color = np.random.choice(self.particle_colors) if len(self.particle_colors) > 1 else self.particle_colors[0]
            
            particles.append({
                'x': x, 'y': y,
                'vx': vx, 'vy': vy,
                'vz': vz,
                'size': np.random.uniform(1, 3),
                'base_size': np.random.uniform(1, 3),
                'brightness': np.random.uniform(0.3, 1.0),
                'pulse_phase': np.random.uniform(0, 2 * np.pi),
                'color': color,
                'life': 1.0,
                'age': 0,
            })
        return particles

    def _spawn_new_particle(self, bass_level=0.0):
        """Spawn a new particle based on particle type"""
        if self.particle_type == ParticleType.SNOW:
            return self._spawn_snow_particle()
        elif self.particle_type == ParticleType.CONTINUOUS_SPAWNING:
            return self._spawn_continuous_particle(bass_level)
        else:
            return self._spawn_standard_particle()
    
    def _spawn_snow_particle(self):
        """Spawn a new snowflake particle"""
        x = self.cx
        y = self.cy
        angle = np.random.uniform(0, 2 * np.pi)
        speed = np.random.uniform(0.5, 2.0)
        vx = speed * np.cos(angle)
        vy = speed * np.sin(angle)
        
        return {
            'x': x, 'y': y,
            'vx': vx, 'vy': vy,
            'size': np.random.uniform(1, 4),
            'brightness': np.random.uniform(0.6, 1.0),
            'pulse_phase': np.random.uniform(0, 2 * np.pi),
            'rotation': np.random.uniform(0, 2 * np.pi),
            'rotation_speed': np.random.uniform(-0.1, 0.1),
            'drift_x': np.random.uniform(-0.2, 0.2),
            'drift_y': np.random.uniform(-0.1, 0.1),
            'life': 1.0,
        }
    
    def _spawn_continuous_particle(self, bass_level=0.0):
        """Spawn a new particle for continuous spawning mode"""
        # Start from spawning area
        if self.spawn_area_width > 0 and self.spawn_area_height > 0:
            x = self.spawn_center_px_x + np.random.uniform(-self.spawn_area_px_width/2, self.spawn_area_px_width/2)
            y = self.spawn_center_px_y + np.random.uniform(-self.spawn_area_px_height/2, self.spawn_area_px_height/2)
        else:
            x = self.spawn_center_px_x
            y = self.spawn_center_px_y
        
        # Bass-responsive speed
        base_speed = np.random.uniform(0.5, 2.0)
        speed_factor = self.enhanced_mode.get("factor", 1.0) if self.enhanced_mode.get("active", False) else 1.0
        speed_multiplier = 1.0 + bass_level * speed_factor
        speed = base_speed * speed_multiplier
        
        angle = np.random.uniform(0, 2 * np.pi)
        vx = speed * np.cos(angle)
        vy = speed * np.sin(angle)
        
        # Bass-responsive size and brightness
        base_size = np.random.uniform(1, 3)
        size_multiplier = 1.0 + bass_level * 0.5
        size = base_size * size_multiplier
        
        base_brightness = np.random.uniform(0.4, 0.8)
        brightness_multiplier = 1.0 + bass_level * 0.5
        brightness = min(1.0, base_brightness * brightness_multiplier)
        
        return {
            'x': x, 'y': y,
            'vx': vx, 'vy': vy,
            'size': size,
            'brightness': brightness,
            'pulse_phase': np.random.uniform(0, 2 * np.pi),
            'life': 1.0,
            'age': 0,
        }
    
    def _spawn_standard_particle(self):
        """Spawn a new standard particle"""
        angle = np.random.uniform(0, 2 * np.pi)
        distance = np.random.uniform(200, 400)
        x = self.cx + distance * np.cos(angle)
        y = self.cy + distance * np.sin(angle)
        
        vx = np.random.uniform(-0.5, 0.5) if self.speed_x == 0 else self.speed_x
        vy = np.random.uniform(-0.5, 0.5) if self.speed_y == 0 else self.speed_y
        vz = np.random.uniform(-0.1, 0.1) if self.speed_z == 0 else self.speed_z
        
        color = np.random.choice(self.particle_colors) if len(self.particle_colors) > 1 else self.particle_colors[0]
        
        return {
            'x': x, 'y': y,
            'vx': vx, 'vy': vy,
            'vz': vz,
            'size': np.random.uniform(1, 3),
            'base_size': np.random.uniform(1, 3),
            'brightness': np.random.uniform(0.3, 1.0),
            'pulse_phase': np.random.uniform(0, 2 * np.pi),
            'color': color,
            'life': 1.0,
            'age': 0,
        }

    def load_audio(self, audio_path: str):
        """Load audio file and extract bass frequencies"""
        print(f"🎵 Loading audio: {audio_path}")
        self.audio_data, self.sample_rate = librosa.load(audio_path, sr=None, mono=True)
        print(f"📊 Audio loaded: {len(self.audio_data)} samples at {self.sample_rate}Hz")
        
        self.bass_frequencies = self._extract_bass_frequencies()
        print(f"🎸 Bass frequencies extracted: {len(self.bass_frequencies)} frames")

    def _extract_bass_frequencies(self):
        """Extract bass frequency energy for each frame"""
        if self.audio_data is None:
            return np.zeros(int(self.duration * self.fps))
        
        samples_per_frame = max(1, int(self.sample_rate / self.fps))
        total_frames = int(self.duration * self.fps)
        
        window = np.hanning(samples_per_frame).astype(np.float32)
        bass_frequencies = np.zeros(total_frames, dtype=np.float32)
        
        bass_low = 0
        bass_high = 250
        
        for i in range(total_frames):
            start_idx = i * samples_per_frame
            end_idx = min(start_idx + samples_per_frame, len(self.audio_data))
            
            if start_idx >= len(self.audio_data):
                bass_frequencies[i] = 0.0
                continue
            
            segment = self.audio_data[start_idx:end_idx].astype(np.float32)
            if len(segment) < samples_per_frame:
                segment = np.pad(segment, (0, samples_per_frame - len(segment)), mode="constant")
            
            segment_windowed = segment * window
            spec = np.fft.rfft(segment_windowed)
            mag = np.abs(spec)
            
            freqs = np.fft.rfftfreq(samples_per_frame, 1/self.sample_rate)
            
            bass_mask = (freqs >= bass_low) & (freqs <= bass_high)
            if np.any(bass_mask):
                bass_energy = np.mean(mag[bass_mask])
            else:
                bass_energy = 0.0
            
            bass_frequencies[i] = bass_energy
        
        max_bass = np.max(bass_frequencies)
        if max_bass > 0:
            bass_frequencies = bass_frequencies / max_bass
        
        return bass_frequencies

    def _get_bass_level_at_frame(self, frame_idx: int) -> float:
        """Get bass level at specific frame"""
        if self.bass_frequencies is None or frame_idx >= len(self.bass_frequencies):
            return 0.0
        return float(self.bass_frequencies[frame_idx])

    def _apply_enhanced_mode(self, bass_level: float) -> float:
        """Apply enhanced mode processing to bass level"""
        if not self.enhanced_mode or not self.enhanced_mode.get("active", False):
            return bass_level
        
        threshold = self.enhanced_mode.get("threshold", 0.3)
        factor = self.enhanced_mode.get("factor", 2.0)
        
        if bass_level >= threshold:
            enhanced_bass = min(1.0, bass_level * factor)
        else:
            enhanced_bass = bass_level
        
        return enhanced_bass

    def _calculate_spawn_rate(self, bass_level: float) -> float:
        """Calculate particles to spawn based on bass level"""
        if self.particle_type != ParticleType.CONTINUOUS_SPAWNING:
            return 0.0
        
        base_spawn = self.steady_spawn_rate * (self.max_particles / 1000.0)
        
        if bass_level > self.bass_threshold:
            bass_spawn = bass_level * 12.0 * (self.max_particles / 1000.0)
        else:
            bass_spawn = bass_level * 3.0 * (self.max_particles / 1000.0)
        
        return base_spawn + bass_spawn

    def _update_particles(self, t: float, frame_idx: int):
        """Update particle system based on particle type"""
        raw_bass_level = self._get_bass_level_at_frame(frame_idx)
        bass_level = self._apply_enhanced_mode(raw_bass_level)
        
        if self.particle_type == ParticleType.SNOW:
            self._update_snow_particles(t, frame_idx, bass_level)
        elif self.particle_type == ParticleType.CONTINUOUS_SPAWNING:
            self._update_continuous_particles(t, frame_idx, bass_level)
        else:
            self._update_standard_particles(t, frame_idx, bass_level)

    def _update_snow_particles(self, t: float, frame_idx: int, bass_level: float):
        """Update snowflake particles with bass-triggered respawning"""
        particles_to_respawn = []
        
        for i, particle in enumerate(self.particles):
            # Add gentle drift
            particle['vx'] += particle['drift_x'] * 0.01
            particle['vy'] += particle['drift_y'] * 0.01
            
            # Add bass-responsive intensity
            if bass_level > self.bass_threshold:
                speed_multiplier = 1.0 + bass_level * 0.5
                particle['vx'] *= speed_multiplier
                particle['vy'] *= speed_multiplier
            
            # Apply air resistance
            particle['vx'] *= 0.999
            particle['vy'] *= 0.999
            
            # Update position
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            
            # Bass-triggered respawning
            if bass_level > self.bass_threshold:
                particle_speed = np.sqrt(particle['vx']**2 + particle['vy']**2)
                speed_multiplier = 1.0 + (particle_speed / 5.0)
                
                base_respawn_probability = (bass_level - self.bass_threshold) * 0.3
                respawn_probability = base_respawn_probability * speed_multiplier
                
                if np.random.random() < respawn_probability:
                    particles_to_respawn.append(i)
            
            # Update rotation
            particle['rotation'] += particle['rotation_speed']
            
            # Update pulse phase and brightness
            particle['pulse_phase'] += 0.05 + bass_level * 0.1
            base_brightness = 0.6 + 0.4 * (0.5 + 0.5 * np.sin(particle['pulse_phase']))
            particle['brightness'] = base_brightness * (0.8 + 0.2 * bass_level)
            
            # Distance-based fading
            distance_from_center = np.sqrt((particle['x'] - self.cx)**2 + (particle['y'] - self.cy)**2)
            max_distance = np.sqrt(self.W**2 + self.H**2) / 2
            fade_factor = max(0.1, 1.0 - (distance_from_center / max_distance))
            particle['life'] = fade_factor
        
        # Handle respawning
        for i in reversed(particles_to_respawn):
            self.particles[i] = self._spawn_snow_particle()
        
        # Spawn additional particles
        if self.particles:
            total_speed = sum(np.sqrt(p['vx']**2 + p['vy']**2) for p in self.particles)
            avg_speed = total_speed / len(self.particles)
            speed_factor = min(2.0, avg_speed / 2.0)
        else:
            speed_factor = 1.0
        
        base_spawn_rate = 0.5 + bass_level * 3.0
        spawn_rate = base_spawn_rate * (1.0 + speed_factor)
        
        for _ in range(int(spawn_rate)):
            if len(self.particles) < self.particle_count * 2:
                self.particles.append(self._spawn_snow_particle())

    def _update_continuous_particles(self, t: float, frame_idx: int, bass_level: float):
        """Update continuous spawning particles"""
        spawn_rate = self._calculate_spawn_rate(bass_level)
        self.spawn_accumulator += spawn_rate
        
        # Spawn new particles
        while self.spawn_accumulator >= 1.0 and len(self.particles) < self.max_particles:
            new_particle = self._spawn_continuous_particle(bass_level)
            self.particles.append(new_particle)
            self.spawn_accumulator -= 1.0
        
        # Update existing particles
        particles_to_remove = []
        
        for i, particle in enumerate(self.particles):
            # Bass-responsive movement
            if bass_level > self.bass_threshold:
                speed_factor = self.enhanced_mode.get("factor", 1.0) if self.enhanced_mode.get("active", False) else 1.0
                speed_multiplier = 1.0 + bass_level * speed_factor * 0.1
                particle['vx'] *= speed_multiplier
                particle['vy'] *= speed_multiplier
            
            # Apply air resistance
            particle['vx'] *= 0.998
            particle['vy'] *= 0.998
            
            # Update position
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            
            # Update age
            particle['age'] += 1
            
            # Update pulse phase and brightness
            particle['pulse_phase'] += 0.05 + bass_level * 0.1
            base_brightness = 0.4 + 0.6 * (0.5 + 0.5 * np.sin(particle['pulse_phase']))
            particle['brightness'] = base_brightness * (0.7 + 0.3 * bass_level)
            
            # Distance-based fading
            distance_from_center = np.sqrt((particle['x'] - self.cx)**2 + (particle['y'] - self.cy)**2)
            max_distance = np.sqrt(self.W**2 + self.H**2) / 2
            fade_factor = max(0.1, 1.0 - (distance_from_center / max_distance))
            particle['life'] = fade_factor
            
            # Remove particles outside frame or too old
            if (particle['x'] < -50 or particle['x'] > self.W + 50 or 
                particle['y'] < -50 or particle['y'] > self.H + 50 or
                particle['age'] > 1000):
                particles_to_remove.append(i)
        
        # Remove particles
        for i in reversed(particles_to_remove):
            self.particles.pop(i)

    def _update_standard_particles(self, t: float, frame_idx: int, bass_level: float):
        """Update standard particles with music-dependent movement"""
        for particle in self.particles:
            # ZEN PARTICLES: No music dependency, just floating around
            if self.particle_type == ParticleType.ZEN:
                # Simple floating movement with gentle drift
                particle['vx'] += np.random.uniform(-0.05, 0.05)
                particle['vy'] += np.random.uniform(-0.05, 0.05)
                
                # Apply gentle air resistance
                particle['vx'] *= 0.998
                particle['vy'] *= 0.998
                
                # Update position
                particle['x'] += particle['vx']
                particle['y'] += particle['vy']
                
                # Update pulse phase and brightness (no music dependency)
                particle['pulse_phase'] += 0.05
                base_brightness = 0.3 + 0.7 * (0.5 + 0.5 * np.sin(particle['pulse_phase']))
                particle['brightness'] = base_brightness
                
                # Handle boundaries for ZEN particles
                if self.bounce:
                    # Bounce behavior
                    if particle['x'] < 0:
                        particle['x'] = 0
                        particle['vx'] = abs(particle['vx'])
                    elif particle['x'] >= self.W:
                        particle['x'] = self.W - 1
                        particle['vx'] = -abs(particle['vx'])
                    
                    if particle['y'] < 0:
                        particle['y'] = 0
                        particle['vy'] = abs(particle['vy'])
                    elif particle['y'] >= self.H:
                        particle['y'] = self.H - 1
                        particle['vy'] = -abs(particle['vy'])
                else:
                    # Random respawn if not bouncing
                    if particle['x'] < 0 or particle['x'] >= self.W or particle['y'] < 0 or particle['y'] >= self.H:
                        particle['x'] = np.random.uniform(0, self.W)
                        particle['y'] = np.random.uniform(0, self.H)
                        particle['vx'] = np.random.uniform(-0.5, 0.5)
                        particle['vy'] = np.random.uniform(-0.5, 0.5)
                        particle['size'] = np.random.uniform(1, 3)
                        particle['brightness'] = np.random.uniform(0.3, 1.0)
                        particle['pulse_phase'] = np.random.uniform(0, 2 * np.pi)
            
            # BOUNCING PARTICLES: Fixed count, bounce back, increased movement with bass
            elif self.particle_type == ParticleType.BOUNCING:
                # Bass-responsive movement (increased excitement with bass)
                if bass_level > self.bass_threshold:
                    # High bass: increased movement and excitement
                    excitement_factor = 1.0 + bass_level * 2.0  # Up to 3x movement
                    particle['vx'] += np.random.uniform(-0.3, 0.3) * excitement_factor
                    particle['vy'] += np.random.uniform(-0.3, 0.3) * excitement_factor
                else:
                    # Low bass: gentle movement
                    particle['vx'] += np.random.uniform(-0.1, 0.1)
                    particle['vy'] += np.random.uniform(-0.1, 0.1)
                
                # Apply air resistance
                particle['vx'] *= 0.995
                particle['vy'] *= 0.995
                
                # Update position
                particle['x'] += particle['vx']
                particle['y'] += particle['vy']
                
                # Update pulse phase and brightness (bass responsive)
                particle['pulse_phase'] += 0.1 + bass_level * 0.3
                base_brightness = 0.3 + 0.7 * (0.5 + 0.5 * np.sin(particle['pulse_phase']))
                particle['brightness'] = base_brightness * (0.7 + 0.3 * bass_level)
                
                # BOUNCE BACK on frame boundaries (no respawn)
                if particle['x'] < 0:
                    particle['x'] = 0
                    particle['vx'] = abs(particle['vx'])
                elif particle['x'] >= self.W:
                    particle['x'] = self.W - 1
                    particle['vx'] = -abs(particle['vx'])
                
                if particle['y'] < 0:
                    particle['y'] = 0
                    particle['vy'] = abs(particle['vy'])
                elif particle['y'] >= self.H:
                    particle['y'] = self.H - 1
                    particle['vy'] = -abs(particle['vy'])
            
            # OTHER PARTICLES: Original music-dependent behavior
            else:
                # Calculate distance from center
                dx = particle['x'] - self.cx
                dy = particle['y'] - self.cy
                distance_from_center = np.sqrt(dx*dx + dy*dy)
                
                # Music-dependent movement logic
                if bass_level > self.bass_threshold:
                    # High bass: outer movement
                    outward_force = bass_level * self.outer_movement_strength * 3.0
                    
                    if distance_from_center > 0:
                        dx_norm = dx / distance_from_center
                        dy_norm = dy / distance_from_center
                    else:
                        angle = np.random.uniform(0, 2 * np.pi)
                        dx_norm = np.cos(angle)
                        dy_norm = np.sin(angle)
                    
                    particle['vx'] += dx_norm * outward_force * 0.05
                    particle['vy'] += dy_norm * outward_force * 0.05
                    
                    particle['vx'] += np.random.uniform(-0.5, 0.5) * bass_level
                    particle['vy'] += np.random.uniform(-0.5, 0.5) * bass_level
                else:
                    # Low bass: inner movement
                    if distance_from_center > 0:
                        inward_force = self.inner_movement_strength * (1.0 - bass_level) * 2.0
                        
                        dx_norm = -dx / distance_from_center
                        dy_norm = -dy / distance_from_center
                        
                        particle['vx'] += dx_norm * inward_force * 0.03
                        particle['vy'] += dy_norm * inward_force * 0.03
                    
                    particle['vx'] += np.random.uniform(-0.1, 0.1)
                    particle['vy'] += np.random.uniform(-0.1, 0.1)
                
                # Apply air resistance
                particle['vx'] *= 0.995
                particle['vy'] *= 0.995
                
                # Update position
                particle['x'] += particle['vx']
                particle['y'] += particle['vy']
                
                # Update pulse phase and brightness
                particle['pulse_phase'] += 0.1 + bass_level * 0.2
                base_brightness = 0.3 + 0.7 * (0.5 + 0.5 * np.sin(particle['pulse_phase']))
                particle['brightness'] = base_brightness * (0.7 + 0.3 * bass_level)
                
                # Update size based on z speed
                if 'vz' in particle:
                    particle['size'] += particle['vz']
                    particle['size'] = max(0.5, min(particle['size'], 10.0))
                
                # Handle boundaries for other particle types
                if self.bounce:
                    # Bounce behavior
                    if particle['x'] < 0:
                        particle['x'] = 0
                        particle['vx'] = abs(particle['vx'])
                    elif particle['x'] >= self.W:
                        particle['x'] = self.W - 1
                        particle['vx'] = -abs(particle['vx'])
                    
                    if particle['y'] < 0:
                        particle['y'] = 0
                        particle['vy'] = abs(particle['vy'])
                    elif particle['y'] >= self.H:
                        particle['y'] = self.H - 1
                        particle['vy'] = -abs(particle['vy'])
                else:
                    # Wrap around or respawn
                    if particle['x'] < 0 or particle['x'] >= self.W or particle['y'] < 0 or particle['y'] >= self.H:
                        if self.particle_type == ParticleType.NO_MUSIC:
                            # Wrap around
                            if particle['x'] < 0 or particle['x'] >= self.W:
                                particle['x'] = np.random.uniform(0, self.W)
                            if particle['y'] < 0 or particle['y'] >= self.H:
                                particle['y'] = np.random.uniform(0, self.H)
                        else:
                            # Respawn from center
                            particle['x'] = self.cx
                            particle['y'] = self.cy
                            angle = np.random.uniform(0, 2 * np.pi)
                            speed = np.random.uniform(1.0, 3.0)
                            particle['vx'] = speed * np.cos(angle)
                            particle['vy'] = speed * np.sin(angle)
                            particle['size'] = np.random.uniform(1, 3)
                            particle['brightness'] = np.random.uniform(0.3, 1.0)
                            particle['pulse_phase'] = np.random.uniform(0, 2 * np.pi)

    def _draw_particles(self, frame):
        """Draw particles based on particle type"""
        if self.particle_type == ParticleType.SNOW:
            return self._draw_snow_particles(frame)
        else:
            return self._draw_standard_particles(frame)

    def _draw_snow_particles(self, frame):
        """Draw snowflake particles"""
        for particle in self.particles:
            x, y = int(particle['x']), int(particle['y'])
            if 0 <= x < self.W and 0 <= y < self.H:
                size = int(particle['size'])
                final_brightness = particle['brightness'] * particle['life']
                brightness = int(255 * final_brightness)
                cv2.circle(frame, (x, y), size, (brightness, brightness, brightness), -1)
        return frame

    def _draw_standard_particles(self, frame):
        """Draw standard particles with colors"""
        for particle in self.particles:
            x, y = int(particle['x']), int(particle['y'])
            if 0 <= x < self.W and 0 <= y < self.H:
                size = int(particle['size'])
                brightness = particle['brightness']
                
                # Apply brightness to color
                color = particle.get('color', (255, 255, 255))
                if isinstance(color, (list, tuple)) and len(color) >= 3:
                    b, g, r = color[0], color[1], color[2]
                    final_color = (
                        int(b * brightness),
                        int(g * brightness), 
                        int(r * brightness)
                    )
                else:
                    gray = int(255 * brightness)
                    final_color = (gray, gray, gray)
                
                cv2.circle(frame, (x, y), size, final_color, -1)
        return frame

    def _draw_bass_indicator(self, frame, frame_idx):
        """Draw bass level indicator on screen"""
        raw_bass_level = self._get_bass_level_at_frame(frame_idx)
        enhanced_bass_level = self._apply_enhanced_mode(raw_bass_level)
        
        # Draw bass level bar
        bar_width = 400
        bar_height = 20
        bar_x = (self.W - bar_width) // 2
        bar_y = 50
        
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (50, 50, 50), -1)
        
        level_width = int(bar_width * enhanced_bass_level)
        if enhanced_bass_level > self.bass_threshold:
            color = (0, 0, 255)  # Red
            text = f"HIGH BASS - {self.particle_type.value.upper()}"
        else:
            color = (255, 0, 0)  # Blue
            text = f"LOW BASS - {self.particle_type.value.upper()}"
        
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + level_width, bar_y + bar_height), color, -1)
        
        # Add text
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(text, font, 0.6, 2)[0]
        text_x = (self.W - text_size[0]) // 2
        text_y = bar_y + bar_height + 30
        cv2.putText(frame, text, (text_x, text_y), font, 0.6, color, 2)
        
        # Add enhanced mode indicator
        if self.enhanced_mode.get("active", False) and raw_bass_level >= self.enhanced_mode.get("threshold", 0.3):
            enhanced_text = f"ENHANCED! (x{self.enhanced_mode.get('factor', 2.0)})"
            enhanced_text_size = cv2.getTextSize(enhanced_text, font, 0.5, 2)[0]
            enhanced_text_x = (self.W - enhanced_text_size[0]) // 2
            enhanced_text_y = text_y + 25
            cv2.putText(frame, enhanced_text, (enhanced_text_x, enhanced_text_y), font, 0.5, (0, 255, 255), 2)
        
        # Add particle count info
        particle_text = f"Particles: {len(self.particles)} | Type: {self.particle_type.value}"
        particle_text_size = cv2.getTextSize(particle_text, font, 0.4, 1)[0]
        particle_text_x = (self.W - particle_text_size[0]) // 2
        particle_text_y = text_y + 50
        cv2.putText(frame, particle_text, (particle_text_x, particle_text_y), font, 0.4, (255, 255, 255), 1)
        
        return frame

    def render_particles(self, output_path: str, audio_path: Optional[str] = None):
        """Render particles video with optional audio"""
        start_time = time.time()
        print(f"🚀 Starting {self.particle_type.value} particles render...")
        
        # Load audio if provided
        if audio_path and os.path.exists(audio_path):
            self.load_audio(audio_path)
        else:
            print("⚠️ No audio file provided, using default movement")
        
        # Calculate total frames
        total_frames = int(self.duration * self.fps)
        frame_times = np.arange(total_frames, dtype=np.float32) / self.fps
        
        # Video writer
        tmp_out = output_path + ".temp.mp4"
        self._ensure_dir(os.path.dirname(output_path))
        writer = cv2.VideoWriter(tmp_out, cv2.VideoWriter_fourcc(*"mp4v"), self.fps, (self.W, self.H))
        if not writer.isOpened():
            raise RuntimeError("Failed to open video writer")
        
        # Main rendering loop
        for i in range(total_frames):
            t = frame_times[i]
            
            # Start with black frame
            frame = self.black_frame.copy()
            
            # Update particles
            self._update_particles(t, i)
            
            # Draw particles
            frame = self._draw_particles(frame)
            
            # Draw bass level indicator
            frame = self._draw_bass_indicator(frame, i)
            
            # Write frame
            writer.write(frame)
            
            # Progress reporting
            if total_frames > 0 and i % max(1, total_frames // 10) == 0:
                elapsed = time.time() - start_time
                fps_actual = (i + 1) / elapsed if elapsed > 0 else 0
                print(f"Progress: {int(100 * i / total_frames)}% | Elapsed: {elapsed:.1f}s | FPS: {fps_actual:.1f} | Particles: {len(self.particles)}")

        writer.release()

        # Finalize
        if os.path.exists(output_path):
            os.remove(output_path)
        os.rename(tmp_out, output_path)
        
        # Audio muxing
        if audio_path and os.path.exists(audio_path):
            self._mux_audio(output_path, audio_path)
        
        total_time = time.time() - start_time
        print(f"✅ Done: {output_path} ({total_time:.1f}s)")

    def _mux_audio(self, video_path: str, audio_path: str):
        """Mux audio into video using ffmpeg"""
        if not audio_path or not os.path.exists(audio_path):
            return
            
        temp_out = video_path + ".with_audio.mp4"
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "320k",
            "-map", "0:v:0", "-map", "1:a:0",
            "-shortest",
            temp_out
        ]
        try:
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if proc.returncode == 0 and os.path.exists(temp_out) and os.path.getsize(temp_out) > 0:
                os.remove(video_path)
                shutil.move(temp_out, video_path)
                print("🔊 Audio muxed into video.")
            else:
                if os.path.exists(temp_out):
                    os.remove(temp_out)
                print("⚠️ ffmpeg failed; leaving video without audio.")
        except Exception as e:
            print(f"⚠️ ffmpeg error: {e}. Leaving video without audio.")

    @staticmethod
    def _ensure_dir(d):
        if d and not os.path.exists(d):
            os.makedirs(d, exist_ok=True)

    # FastAPI Integration Methods
    def get_status(self) -> Dict[str, Any]:
        """Get current particle system status for API"""
        return {
            "particle_type": self.particle_type.value,
            "particle_count": len(self.particles),
            "max_particles": self.max_particles,
            "config": {
                "width": self.W,
                "height": self.H,
                "fps": self.fps,
                "duration": self.duration,
                "bass_threshold": self.bass_threshold,
                "enhanced_mode": self.enhanced_mode
            },
            "audio_loaded": self.audio_data is not None
        }

    def update_config(self, new_config: Dict[str, Any]):
        """Update particle system configuration"""
        for key, value in new_config.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                # Update instance variables
                if key == 'width':
                    self.W = int(value)
                elif key == 'height':
                    self.H = int(value)
                elif key == 'fps':
                    self.fps = int(value)
                elif key == 'particle_count':
                    self.particle_count = int(value)
                elif key == 'duration':
                    self.duration = float(value)
                elif key == 'bass_threshold':
                    self.bass_threshold = float(value)
                elif key == 'enhanced_mode':
                    self.enhanced_mode = value

    def change_particle_type(self, new_type: ParticleType):
        """Change particle type and reinitialize"""
        self.particle_type = new_type
        self.particles = self._init_particles()
        self.spawn_accumulator = 0.0

    def get_available_particle_types(self) -> List[str]:
        """Get list of available particle types"""
        return [pt.value for pt in ParticleType]

    def get_particle_type_info(self, particle_type: ParticleType) -> Dict[str, str]:
        """Get information about a specific particle type"""
        info_map = {
            ParticleType.SNOW: {
                "name": "Snow Particles",
                "description": "Snowflake particles with bass-triggered respawning and outward movement",
                "features": ["Bass-triggered respawning", "Outward movement", "Distance-based fading", "Rotation effects"]
            },
            ParticleType.ZEN: {
                "name": "Zen Particles",
                "description": "Floating particles that bounce back on screen frames or respawn randomly (no music dependency)",
                "features": ["No music dependency", "Gentle floating movement", "Bounce back or random respawn", "Pulsing brightness"]
            },
            ParticleType.ENHANCED: {
                "name": "Enhanced Particles",
                "description": "Advanced particles with enhanced mode and multiple features",
                "features": ["Enhanced mode", "Color support", "Size changes", "Advanced movement"]
            },
            ParticleType.BOUNCING: {
                "name": "Bouncing Particles",
                "description": "Fixed count particles that bounce back on frame boundaries with increased movement during bass",
                "features": ["Fixed particle count", "Frame boundary bouncing", "Bass-responsive excitement", "No respawning"]
            },
            ParticleType.CONTINUOUS_SPAWNING: {
                "name": "Continuous Spawning",
                "description": "Particles that continuously spawn based on bass levels",
                "features": ["Continuous spawning", "Bass-responsive spawn rate", "Particle limits", "Age tracking"]
            },
            ParticleType.NO_MUSIC: {
                "name": "No Music Particles",
                "description": "Static particles without music dependency",
                "features": ["No music dependency", "Screen wrapping", "Basic movement"]
            }
        }
        return info_map.get(particle_type, {"name": "Unknown", "description": "Unknown particle type", "features": []})


# FastAPI Integration Functions
def create_particle_system(particle_type: str, config: Optional[Dict[str, Any]] = None) -> UnifiedParticleSystem:
    """Create a particle system instance for FastAPI"""
    try:
        pt = ParticleType(particle_type)
        particle_config = ParticleConfig()
        
        if config:
            for key, value in config.items():
                if hasattr(particle_config, key):
                    setattr(particle_config, key, value)
        
        return UnifiedParticleSystem(particle_type=pt, config=particle_config)
    except ValueError:
        raise ValueError(f"Invalid particle type: {particle_type}. Available types: {[pt.value for pt in ParticleType]}")

def get_particle_type_list() -> List[Dict[str, Any]]:
    """Get list of all available particle types with descriptions"""
    system = UnifiedParticleSystem()
    return [
        {
            "type": pt.value,
            **system.get_particle_type_info(pt)
        }
        for pt in ParticleType
    ]


# Test functions
def test_all_particle_types():
    """Test all particle types"""
    test_config = ParticleConfig(
        width=1280,
        height=720,
        fps=30,
        duration=5.0,
        particle_count=50
    )
    
    for particle_type in ParticleType:
        print(f"\n🧪 Testing {particle_type.value} particles...")
        system = UnifiedParticleSystem(particle_type=particle_type, config=test_config)
        output_path = f"test_{particle_type.value}_particles.mp4"
        system.render_particles(output_path)
        print(f"✅ {particle_type.value} test completed: {output_path}")

if __name__ == "__main__":
    test_all_particle_types()
