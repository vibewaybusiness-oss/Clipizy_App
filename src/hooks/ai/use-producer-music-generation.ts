import { useCallback } from 'react';
import { useToast } from '../ui/use-toast';
import type { MusicTrack } from '@/types/domains/music';

interface UseProducerMusicGenerationProps {
  musicClipState: any;
  musicTracks: any;
  projectManagement: any;
  setShowOnboardingLoading: (loading: boolean) => void;
}

export function useProducerMusicGeneration({
  musicClipState,
  musicTracks,
  projectManagement,
  setShowOnboardingLoading
}: UseProducerMusicGenerationProps) {
  const { toast } = useToast();

  const handleGenerateMusicWithProducerAI = useCallback(async (
    selectedGenre?: string, 
    isInstrumental?: boolean
  ) => {
    musicClipState.actions.setIsUploadingTracks(true);
    
    try {
      let currentProjectId = projectManagement.state.currentProjectId;
      console.log('🎵 ProducerAI: Project management state:', {
        currentProjectId: projectManagement.state.currentProjectId,
        isProjectCreated: projectManagement.state.isProjectCreated,
        isLoadingProject: projectManagement.state.isLoadingProject
      });
      
      if (projectManagement.state.isLoadingProject) {
        console.log('🎵 ProducerAI: Project is currently loading, waiting...');
        await new Promise(resolve => setTimeout(resolve, 1000));
        currentProjectId = projectManagement.state.currentProjectId;
        console.log('🎵 ProducerAI: After waiting, currentProjectId:', currentProjectId);
      }
      
      if (!currentProjectId) {
        console.log('🎵 ProducerAI: No existing project found, creating new one...');
        currentProjectId = await projectManagement.actions.createProject();
        console.log('🎵 ProducerAI: New project created with ID:', currentProjectId);
        
        // Project ID is now managed through backend storage
        console.log('🔧 ProducerAI: Project created with ID:', currentProjectId);
      } else {
        console.log('🎵 ProducerAI: Using existing project ID for music generation:', currentProjectId);
      }
      
      // Use ProducerAI for music generation
      const musicPrompt = musicClipState.state.musicPrompt;
      const lyrics = musicClipState.state.lyrics;
      const isInstrumentalMode = isInstrumental || musicClipState.state.isInstrumental;
      
      console.log('🎵 ProducerAI: Generating music with ProducerAI:', {
        prompt: musicPrompt,
        lyrics: lyrics,
        isInstrumental: isInstrumentalMode,
        tracksToGenerate: musicClipState.state.musicTracksToGenerate
      });
      
      const generatedTracks: MusicTrack[] = [];
      
      for (let i = 0; i < musicClipState.state.musicTracksToGenerate; i++) {
        const trackId = `producer-generated-${Date.now()}-${i}`;
        const trackNumber = musicTracks?.tracks.length + i + 1;
        const trackName = `ProducerAI Track ${trackNumber}`;
        
        try {
          // Call ProducerAI router directly
          const response = await fetch('/api/ai/producer/generate', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            },
            body: JSON.stringify({
              project_id: currentProjectId,
              genre: selectedGenre,
              is_instrumental: isInstrumentalMode,
              style: musicPrompt,
              mood: lyrics
            }),
          });

          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Music generation failed');
          }

          const data = await response.json();
          
          if (data.success && data.uploaded_files && data.uploaded_files.length > 0) {
            const uploadedFile = data.uploaded_files[0];
            
            // Debug: Log the uploaded file structure to help troubleshoot duration issues
            console.log('🎵 ProducerAI: Uploaded file structure:', {
              s3_url: uploadedFile.s3_url,
              filename: uploadedFile.filename,
              size: uploadedFile.size,
              track_record: uploadedFile.track_record,
              track_metadata: uploadedFile.track_record?.track_metadata,
              duration_from_metadata: uploadedFile.track_record?.track_metadata?.duration
            });
            
            const track: MusicTrack = {
              id: trackId,
              file: new File([], trackName, { type: 'audio/wav' }),
              url: uploadedFile.s3_url,
              duration: uploadedFile.track_record?.track_metadata?.duration || 30, // Use actual duration from backend
              name: trackName,
              prompt: musicPrompt,
              videoDescription: '',
              generatedAt: new Date(),
              genre: selectedGenre || 'ProducerAI Generated',
              isGenerated: true,
              status: 'completed',
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
              isInstrumental: isInstrumentalMode,
              lyrics: lyrics || '',
              s3_url: uploadedFile.s3_url,
              filename: uploadedFile.filename,
              size: uploadedFile.size,
              generation_method: 'producer_ai',
              metadata: uploadedFile.track_record?.track_metadata || {}
            };
            
            generatedTracks.push(track);
            
            console.log('🎵 ProducerAI: Generated track:', {
              id: trackId,
              name: trackName,
              s3_url: uploadedFile.s3_url,
              size: uploadedFile.size
            });
          } else {
            throw new Error(data.error || 'No files generated');
          }
          
        } catch (error) {
          console.error(`🎵 ProducerAI: Error generating track ${i + 1}:`, error);
          
          // Create a failed track entry
          const failedTrack: MusicTrack = {
            id: trackId,
            file: new File([], trackName, { type: 'audio/wav' }),
            url: '',
            duration: 0,
            name: trackName,
            prompt: musicPrompt,
            videoDescription: '',
            generatedAt: new Date(),
            genre: selectedGenre || 'ProducerAI Generated',
            isGenerated: true,
            status: 'failed',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            isInstrumental: isInstrumentalMode,
            lyrics: lyrics || '',
            generation_method: 'producer_ai',
            error: error instanceof Error ? error.message : 'Unknown error'
          };
          
          generatedTracks.push(failedTrack);
        }
      }
      
      // Add all generated tracks to the music tracks list
      if (generatedTracks.length > 0) {
        musicTracks.addTracks(generatedTracks);
        
        const successCount = generatedTracks.filter(t => t.status === 'completed').length;
        const failCount = generatedTracks.filter(t => t.status === 'failed').length;
        
        if (successCount > 0) {
          // Tracks are already added to the state and will be persisted automatically
          console.log('🎵 ProducerAI: Generated tracks added to state, persistence handled automatically');
          
          toast({
            title: "Music Generated Successfully",
            description: `Generated ${successCount} track(s) using ProducerAI. ${failCount > 0 ? `${failCount} failed.` : ''}`,
          });
        } else {
          toast({
            variant: "destructive",
            title: "Music Generation Failed",
            description: "Failed to generate music tracks. Please try again.",
          });
        }
      }
      
    } catch (error) {
      console.error('🎵 ProducerAI: Error in music generation:', error);
      toast({
        variant: "destructive",
        title: "Generation Failed",
        description: error instanceof Error ? error.message : "Failed to generate music. Please try again.",
      });
    } finally {
      musicClipState.actions.setIsUploadingTracks(false);
      setShowOnboardingLoading(false);
    }
  }, [musicClipState, musicTracks, projectManagement, toast, setShowOnboardingLoading]);

  return {
    handleGenerateMusicWithProducerAI
  };
}
