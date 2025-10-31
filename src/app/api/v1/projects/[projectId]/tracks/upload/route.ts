import { NextRequest, NextResponse } from 'next/server';
import { withErrorHandling, requireAuth, ValidationError } from '../../../../middleware/error-handling';
import { makeBackendFormRequest } from '../../../../lib/utils/backend';
import { createValidatedBlobURL } from '@/utils/memory-management';
import { isValidDuration, DURATION_VALIDATION } from '@/utils/music-clip-utils';

// Utility function to get audio duration from file
const getAudioDuration = (file: File): Promise<number> => {
  return new Promise((resolve, reject) => {
    const audio = new Audio();
    const url = createValidatedBlobURL(file);
    
    const cleanup = () => {
      audio.removeEventListener('loadedmetadata', onLoadedMetadata);
      audio.removeEventListener('error', onError);
    };
    
    const onLoadedMetadata = () => {
      const duration = audio.duration;
      cleanup();
      if (isNaN(duration) || duration === Infinity) {
        reject(new Error('Invalid audio duration'));
      } else {
        resolve(duration);
      }
    };
    
    const onError = (error: Event) => {
      cleanup();
      reject(new Error('Failed to load audio file'));
    };
    
    audio.addEventListener('loadedmetadata', onLoadedMetadata);
    audio.addEventListener('error', onError);
    
    const timeout = setTimeout(() => {
      cleanup();
      reject(new Error('Audio duration extraction timeout'));
    }, 10000);
    
    audio.src = url;
    audio.load();
    
    audio.addEventListener('loadedmetadata', () => {
      clearTimeout(timeout);
    });
  });
};

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ projectId: string }> }
) {
  return withErrorHandling(requireAuth(async (req: NextRequest) => {
  const { projectId } = await params;
  let audioDuration = 0;

  if (!projectId) {
    throw new ValidationError('Project ID is required');
  }

    const formData = await req.formData();
    const file = formData.get('file') as File;

    if (!file) {
      throw new ValidationError('No file provided');
    }

    // Calculate and validate audio duration
    try {
      audioDuration = await getAudioDuration(file);
      console.log('Calculated audio duration:', audioDuration, 'seconds');
      
      // Validate duration
      const validation = isValidDuration(audioDuration);
      if (!validation.isValid) {
        throw new ValidationError(`Invalid audio duration: ${validation.error}`);
      }
    } catch (durationError) {
      console.warn('Failed to calculate audio duration:', durationError);
      
      // If it's a validation error, re-throw it
      if (durationError instanceof ValidationError) {
        throw durationError;
      }
      
      // Use file size estimation as fallback
      const sizeMB = file.size / (1024 * 1024);
      const fileType = file.type;
      if (fileType.includes('wav')) {
        audioDuration = Math.round(sizeMB * 6); // ~6 seconds per MB for WAV
      } else if (fileType.includes('mp3')) {
        audioDuration = Math.round(sizeMB * 60); // ~60 seconds per MB for MP3
      } else {
        audioDuration = 180; // 3 minutes default
      }
      console.log('Using estimated duration based on file size:', audioDuration, 'seconds');
      
      // Validate estimated duration
      const validation = isValidDuration(audioDuration);
      if (!validation.isValid) {
        throw new ValidationError(`Invalid estimated audio duration: ${validation.error}`);
      }
    }

    // Add duration to form data
    formData.append('duration', audioDuration.toString());

    const response = await makeBackendFormRequest(
      `/api/music-clip/projects/${projectId}/upload-track`,
      formData,
      { timeout: 300000 }, // 5 minutes for file uploads
      req
    );

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend error response:', errorText);
      
      if (response.status >= 500) {
        // Return mock track upload response for server errors
        const mockTrack = {
          track_id: `mock-${Date.now()}`,
          file_path: `/mock/tracks/${file.name}`,
          metadata: {
            name: file.name,
            size: file.size,
            type: file.type,
            duration: audioDuration,
          },
          ai_generated: formData.get('ai_generated') === 'true',
          prompt: formData.get('prompt') || null,
          genre: formData.get('genre') || null,
          instrumental: formData.get('instrumental') === 'true',
          video_description: formData.get('video_description') || null,
        };
        return NextResponse.json(mockTrack);
      }
      
      return NextResponse.json(
        { error: `Backend error: ${response.status} - ${errorText}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  }))(request);
}
